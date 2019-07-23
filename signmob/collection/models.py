from django.contrib.gis.db import models
from django.urls import reverse
from django.utils import timezone

from schedule.models import Calendar, Occurrence, Event

from signmob.users.models import User


class CollectionGroupMember(models.Model):
    group = models.ForeignKey("CollectionGroup", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Ortsgruppenmitglied'
        verbose_name_plural = 'Ortsgruppenmitglieder'
        unique_together = ['group', 'user']

    def __str__(self):
        return self.user.name


class CollectionGroup(models.Model):
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    channel = models.CharField(max_length=255, blank=True)

    geo = models.PointField(null=True, blank=True, geography=True)

    members = models.ManyToManyField(User, through=CollectionGroupMember)

    calendar = models.ForeignKey(
        Calendar, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = 'Ortsgruppe'
        verbose_name_plural = 'Ortsgruppen'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('collection:collectiongroup-detail', kwargs={'pk': self.pk})


class CollectionLocation(models.Model):
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    address = models.TextField(blank=True)
    geo = models.PointField(null=True, blank=True, geography=True)

    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)

    accumulation = models.BooleanField(default=False)

    events = models.ManyToManyField(Event, blank=True)
    email = models.EmailField(blank=True)
    user = models.ForeignKey(
        User, blank=True, null=True,
        on_delete=models.SET_NULL
    )
    needs_check = models.BooleanField(default=False)
    report = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Sammelort'
        verbose_name_plural = 'Sammelorte'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('collection:collectionlocation-report', kwargs={'pk': self.pk})


class CollectionEventMember(models.Model):
    event = models.ForeignKey("CollectionEvent", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    note = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Sammelterminteilnehmer/in'
        verbose_name_plural = 'Sammelterminteilnehmende'
        ordering = ('start', '-end')

    def __str__(self):
        return '{} bei {}'.format(self.user, self.event)


class CollectionEvent(models.Model):
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    geo = models.PointField(null=True, blank=True, geography=True)

    group = models.ForeignKey(
        CollectionGroup, null=True, blank=True,
        on_delete=models.SET_NULL
    )

    event_occurence = models.ForeignKey(
        Occurrence, null=True, on_delete=models.CASCADE
    )
    members = models.ManyToManyField(User, through=CollectionEventMember)

    class Meta:
        verbose_name = 'Sammeltermin'
        verbose_name_plural = 'Sammeltermine'

    def __str__(self):
        return self.name

    @property
    def start(self):
        return self.event_occurence.start

    @property
    def end(self):
        return self.event_occurence.end

    def get_absolute_url(self):
        return reverse('collection:collectionevent-join', kwargs={'pk': self.pk})


class CollectionResult(models.Model):
    amount = models.IntegerField(default=0)

    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    comment = models.TextField(blank=True)

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    group = models.ForeignKey(
        CollectionGroup, null=True, blank=True, on_delete=models.SET_NULL
    )
    location = models.ForeignKey(
        CollectionLocation, null=True, blank=True, on_delete=models.SET_NULL
    )
    event = models.ForeignKey(
        CollectionEvent, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = 'Sammelergebnis'
        verbose_name_plural = 'Sammelergebnisse'

    def __str__(self):
        return '{} ({} - {})'.format(self.amount, self.start, self.end)
