from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import (
    CollectionGroup,
    CollectionEvent,
    CollectionLocation,
    CollectionResult,
    CollectionEventMember,
    CollectionGroupMember,
)


class CollectionEventMemberInline(admin.StackedInline):
    model = CollectionEventMember


class CollectionEventAdmin(LeafletGeoAdmin):
    display_raw = True
    inlines = [CollectionEventMemberInline]
    save_on_top = True


class CollectionLocationAdmin(LeafletGeoAdmin):
    display_raw = True
    raw_id_fields = ('events',)


class CollectionGroupMemberInline(admin.StackedInline):
    model = CollectionGroupMember


class CollectionGroupAdmin(LeafletGeoAdmin):
    inlines = [CollectionGroupMemberInline]
    save_on_top = True


class CollectionGroupMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'joined')
    list_filter = ('responsible', 'group',)
    date_hierarchy = 'joined'


class CollectionEventMemberAdmin(admin.ModelAdmin):
    pass


class CollectionResultAdmin(admin.ModelAdmin):
    pass


admin.site.register(CollectionGroup, CollectionGroupAdmin)
admin.site.register(CollectionEvent, CollectionEventAdmin)
admin.site.register(CollectionLocation, CollectionLocationAdmin)
admin.site.register(CollectionResult, CollectionResultAdmin)
admin.site.register(CollectionGroupMember, CollectionGroupMemberAdmin)
admin.site.register(CollectionEventMember, CollectionEventMemberAdmin)
