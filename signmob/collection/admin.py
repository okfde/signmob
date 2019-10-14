from datetime import datetime, timedelta

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from leaflet.admin import LeafletGeoAdmin

from schedule.admin import EventAdmin
from schedule.models import Event, Occurrence

from signmob.admin_utils import SendMailMixin

from .models import (
    CollectionGroup,
    CollectionEvent,
    CollectionLocation,
    CollectionResult,
    CollectionEventMember,
    CollectionGroupMember,
)
from .tasks import material_sent_task
from .utils import get_occurrence


class CollectionEventMemberInline(admin.StackedInline):
    model = CollectionEventMember


class CollectionEventAdmin(SendMailMixin, LeafletGeoAdmin):
    display_raw = False
    inlines = [CollectionEventMemberInline]
    save_on_top = True
    readonly_fields = ('start_time', 'end_time',)
    list_display = ('name', 'start', 'end', 'group')
    list_filter = ('group',)
    date_hierarchy = 'event_occurence__start'
    fieldsets = (
        (None, {
            'fields': (
                'name', 'description', 'start_time', 'end_time',
                'event_occurence', 'geo'
            )
        }),
        ('Gruppe', {
            'fields': ('group',),
            'classes': ('collapse',)
        }),
    )
    actions = ['send_mail']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('event_occurence', 'group')
        return qs

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                'from-event/<int:event_id>/',
                self.admin_site.admin_view(self.create_from_event),
                name='collection-collectionevent-create_from_event'
            ),
        ]
        return my_urls + urls

    def create_from_event(self, request, event_id):
        event = Event.objects.get(pk=event_id)

        if event.rule:
            date = datetime(*[int(x) for x in request.POST['date'].split('-')])
        else:
            date = event.start

        occurrence = get_occurrence(event, date)
        if occurrence is None:
            self.message_user(request, 'Konnte an diesem Datum keinen geplanten Termin finden!')
            return redirect('admin:schedule_event_change', event_id)
        occurrence.save()

        try:
            group = CollectionGroup.objects.get(
                calendar=event.calendar
            )
        except CollectionGroup.DoesNotExist:
            group = None

        try:
            c_event = CollectionEvent.objects.filter(
                event_occurence=occurrence
            ).get()
        except CollectionEvent.DoesNotExist:
            c_event = CollectionEvent.objects.create(
                name=event.title,
                description=event.description,
                geo=group.geo if group is not None else None,
                group=group,
                event_occurence=occurrence
            )
        return redirect('admin:collection_collectionevent_change', c_event.id)

    def _get_send_mail_user_ids(self, queryset):
        # Send to all members of event, deduplicate
        qs = CollectionEventMember.objects.filter(event__in=queryset)
        return list(set(qs.values_list('user_id', flat=True)))


class CollectionLocationAdmin(LeafletGeoAdmin):
    display_raw = True
    raw_id_fields = ('events',)
    date_hierarchy = 'start'
    list_display = (
        'name', 'address', 'start', 'end', 'needs_check',
        'send_material'
    )
    list_filter = (
        'needs_check', 'accumulation',
        'start',
    )
    actions = ['set_material_sent']

    def set_material_sent(self, request, queryset):
        count = 0
        for loc in queryset.filter(send_material=True, start__isnull=True):
            loc.start = timezone.now().date() + timedelta(days=1)
            loc.save()
            if loc.email:
                count += 1
                material_sent_task.delay(loc.id)
        self.message_user(request, _("%d emails sent to location owners.") % count)
    set_material_sent.short_description = _('Send material delivery notification')


class CollectionGroupMemberInline(admin.StackedInline):
    model = CollectionGroupMember


class CollectionGroupAdmin(SendMailMixin, LeafletGeoAdmin):
    inlines = [CollectionGroupMemberInline]
    save_on_top = True
    actions = ['send_mail']

    def _get_send_mail_user_ids(self, queryset):
        # Send to all members of all selected groups
        qs = CollectionGroupMember.objects.filter(group__in=queryset)
        return list(qs.values_list('user_id', flat=True))


class CollectionGroupMemberAdmin(SendMailMixin, admin.ModelAdmin):
    list_display = ('user', 'group', 'joined', 'responsible')
    list_filter = ('responsible', 'group',)
    date_hierarchy = 'joined'
    actions = ['send_mail']

    def _get_send_mail_user_ids(self, queryset):
        # Send to all selected members
        return list(queryset.values_list('user_id', flat=True))


class CollectionEventMemberAdmin(SendMailMixin, admin.ModelAdmin):
    date_hierarchy = 'start'
    list_display = ('user', 'event', 'start', 'end')
    list_filter = ('event__group',)
    actions = ['send_mail']

    def _get_send_mail_user_ids(self, queryset):
        # Send to all selected members, deduplicate
        return list(set(queryset.values_list('user_id', flat=True)))


class CollectionResultAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Wie viel wurde gesammelt?', {
            'fields': (
                'amount',
                'comment',
            )
        }),
        ('Wann wurde gesammelt?', {
            'fields': ('event', 'start', 'end'),
        }),
        ('Von wem wurde gesammelt?', {
            'fields': ('group', 'user',),
        }),
        ('Falls es ein fester Sammelort war', {
            'fields': ('location',),
        }),
    )


admin.site.register(CollectionGroup, CollectionGroupAdmin)
admin.site.register(CollectionEvent, CollectionEventAdmin)
admin.site.register(CollectionLocation, CollectionLocationAdmin)
admin.site.register(CollectionResult, CollectionResultAdmin)
admin.site.register(CollectionGroupMember, CollectionGroupMemberAdmin)
admin.site.register(CollectionEventMember, CollectionEventMemberAdmin)


class CustomEventAdmin(EventAdmin):
    list_filter = ('calendar',) + EventAdmin.list_filter


admin.site.unregister(Event)
admin.site.register(Event, CustomEventAdmin)


class CustomOccurrenceAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(Occurrence)
admin.site.register(Occurrence, CustomOccurrenceAdmin)
