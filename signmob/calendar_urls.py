from django.urls import path
from django.views.decorators.clickjacking import xframe_options_exempt

from schedule.views import CalendarByPeriodsView

from signmob.utils import NextThreeWeeks
from signmob.views import OccurrencePreview

app_name = 'schedule'
urlpatterns = [
    path(
        "calendar/next/<slug:calendar_slug>/",
        xframe_options_exempt(
            CalendarByPeriodsView.as_view(template_name='schedule/three_weeks.html')
        ),
        name='next_three_weeks',
        kwargs={'period': NextThreeWeeks}
    ),

    # urls for unpersisted occurrences
    path(
        'occurrence/<int:event_id>/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>/<int:second>/',
        OccurrencePreview.as_view(),
        name='occurrence_by_date'
    ),
]
