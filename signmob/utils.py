import datetime

import pytz

from django.utils import timezone

from schedule.periods import Period


class NextThreeWeeks(Period):
    """
    The Week period that has functions for retrieving Day periods within it
    """
    def __init__(self, events, date=None, parent_persisted_occurrences=None,
                 occurrence_pool=None, tzinfo=pytz.utc):
        self.tzinfo = pytz.utc  # self._get_tzinfo(tzinfo)
        if date is None:
            date = timezone.now().astimezone(self.tzinfo)
        start, end = self._get_range(date)
        super().__init__(events, start, end, parent_persisted_occurrences,
                         occurrence_pool, tzinfo=self.tzinfo)

    def _get_range(self, date):
        if isinstance(date, datetime.datetime):
            date = date.date()
        # Adjust the start datetime to midnight of the week datetime
        naive_start = datetime.datetime.combine(date, datetime.time.min)
        naive_end = naive_start + datetime.timedelta(days=7 * 3)

        if self.tzinfo is not None:
            local_start = self.tzinfo.localize(naive_start)
            local_end = self.tzinfo.localize(naive_end)
            start = local_start.astimezone(pytz.utc)
            end = local_end.astimezone(pytz.utc)
        else:
            start = naive_start
            end = naive_end

        return start, end
