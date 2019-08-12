import datetime

from django.views.generic import FormView
from django.views.generic.detail import DetailView
from django import forms
from django.shortcuts import get_object_or_404, Http404, redirect
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from schedule.models import Event
from schedule.views import OccurrenceMixin

from signmob.users.utils import send_mail


class OccurrencePreview(OccurrenceMixin, DetailView):
    template_name = 'schedule/occurrence.html'

    def get_object(self, queryset=None):
        event = get_object_or_404(Event, id=self.kwargs['event_id'])
        date = timezone.make_aware(
            datetime.datetime(
                self.kwargs['year'],
                self.kwargs['month'],
                self.kwargs['day'],
                self.kwargs['hour'],
                self.kwargs['minute'],
                self.kwargs['second']
            ), timezone.utc
        )

        occurrence = event.get_occurrence(date)
        if occurrence is None:
            raise Http404
        return occurrence

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context = {
            'event': self.object.event,
            'occurrence': self.object,
        }
        return context


class ContactForm(forms.Form):
    name = forms.CharField(
        label='Dein Name',
    )
    email = forms.EmailField(
        label='Deine E-Mail',
    )
    message = forms.CharField(
        label='Deine Nachricht',
        widget=forms.Textarea(attrs={
            'rows': '4',
        })
    )

    def save(self):
        send_mail(
            'Neue Nachricht via Kontaktformular',
            'Von: {name} <{email}>\n\n{message}'.format(
                **self.cleaned_data
            ),
            settings.CONTACT_EMAIL
        )


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'contact.html'

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        form.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse('contact-thanks')
