import datetime
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404, Http404
from django.utils import timezone

from schedule.models import Event
from schedule.views import OccurrenceMixin


class OccurrencePreview(OccurrenceMixin, DetailView):
    template_name = 'schedule/occurrence.html'

    def get_object(self, queryset=None):
        event = get_object_or_404(Event, id=self.kwargs['event_id'])
        date = timezone.make_aware(
            datetime.datetime(
                int(self.kwargs['year']),
                int(self.kwargs['month']),
                int(self.kwargs['day']),
                int(self.kwargs['hour']),
                int(self.kwargs['minute']),
                int(self.kwargs['second'])
            ), None
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
