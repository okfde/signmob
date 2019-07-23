from datetime import datetime

from django import forms
from django.utils import timezone
from django.db.models import Q
from django.core.validators import MinValueValidator, MaxValueValidator

from leaflet.forms.fields import PointField

from signmob.users.forms import CustomSignupForm

from .models import (
    CollectionGroupMember, CollectionLocation,
    CollectionEventMember
)
from .signals import group_joined, location_created, location_reported


class GroupSignupForm(CustomSignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password1']

    def save(self, request, group):
        user = super().save(request)
        CollectionGroupMember.objects.create(
            group=group,
            user=user
        )
        group_joined.send(
            sender=group.__class__,
            user=user,
            group=group
        )

        return user


class CollectionLocationForm(forms.ModelForm):
    name = forms.CharField(
        label='Name des Orts',
        help_text='Zum Beispiel: Bäckerei Müller an der Hauptstraße'
    )
    address = forms.CharField(
        label='Adresse',
        help_text='Bitte gib Straße, Hausnr. und PLZ an',
        widget=forms.Textarea(attrs={
            'rows': '2'
        }),
    )
    description = forms.CharField(
        label='Weitere Details: z.B. wann kann man hier unterschreiben?',
        help_text='Bitte gib Öffnungszeiten an und weitere Details, falls der Ort schwerer zu finden ist.',
        widget=forms.Textarea(attrs={
            'rows': '3'
        }),
    )

    geo = PointField(
        label='Genauer Ort auf der Karte',
        help_text=(
            'Bitte zoom an den Ort heran. Dann klicke links auf den Marker und setze ihn möglichst '
            'genau auf den Ort der Unterschriftenliste.'
        )
    )
    email = forms.EmailField(
        label='Deine E-Mail-Adresse',
        help_text='Optional. Falls wir Rückfragen zu diesem Ort haben, können wir dich kontaktieren.',
        required=False
    )

    class Meta:
        model = CollectionLocation
        fields = ('name', 'geo', 'address', 'description', 'email',)

    def save(self, request):
        obj = super().save(commit=False)
        if request.user.is_authenticated:
            obj.user = request.user
        obj.start = timezone.now()

        # only needs check if non-staff created it
        obj.needs_check = not request.user.is_authenticated
        obj.save()

        location_created.send(
            sender=obj.__class__,
            location=obj,
        )

        return obj


class CollectionLocationReportForm(forms.Form):
    report = forms.CharField(
        label='Was ist mit diesem Sammelort los?',
        help_text="Ist die Unterschriftenliste voll? Ist sie nicht mehr da? Erzähl's uns!",
        widget=forms.Textarea(
            attrs={
                'rows': '3'
            }
        )
    )

    def save(self, location):
        report = self.cleaned_data['report']

        location.needs_check = True
        location.report = '{date}\n{report}\n\n---\n\n{rest}'.format(
            date=timezone.now().isoformat(),
            report=report,
            rest=location.report
        )
        location.save()
        location_reported.send(
            sender=location.__class__,
            location=location
        )
        return location


class CollectionEventJoinForm(forms.Form):
    start = forms.TimeField(
        label='Teilnahme ab',
        required=True,
    )
    end = forms.TimeField(
        label='Teilnahme bis',
        help_text='Falls du noch mal wieder kommst, kannst du dieses Formular auch mehrfach ausfüllen.',
        required=True,
    )
    note = forms.CharField(
        label='Optionale Nachricht',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': '2'
            }
        )
    )

    def __init__(self, *args, event=None, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)
        local_start = timezone.localtime(
            self.event.start
        ).time()
        local_end = timezone.localtime(
            self.event.end
        ).time()
        self.fields['start'].initial = local_start
        self.fields['end'].initial = local_end
        self.fields['start'].validators.append(
            MinValueValidator(local_start)
        )
        self.fields['end'].validators.append(
            MaxValueValidator(local_end)
        )

    def save(self, user):
        date = self.event.start.date()
        start_date = datetime.combine(date, self.cleaned_data['start'])
        end_date = datetime.combine(date, self.cleaned_data['end'])
        current_tz = timezone.get_current_timezone()
        start_date = current_tz.localize(start_date)
        end_date = current_tz.localize(end_date)

        overlapping_events = CollectionEventMember.objects.filter(
            event=self.event,
            user=user,
        ).filter(
            (Q(start__gte=start_date) & Q(end__lte=start_date)) |
            (Q(start__lte=end_date) & Q(end__gte=end_date))
        )
        for oe in overlapping_events:
            start_date = min(start_date, oe.start)
            end_date = max(end_date, oe.end)
        overlapping_events.delete()

        event_member = CollectionEventMember.objects.create(
            event=self.event,
            user=user,
            start=start_date,
            end=end_date,
            note=self.cleaned_data['note'],
        )
        return event_member
