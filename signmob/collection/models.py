from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.conf import settings

from schedule.models import Calendar, Occurrence, Event

from signmob.users.models import User


class CollectionGroupMember(models.Model):
    group = models.ForeignKey("CollectionGroup", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined = models.DateTimeField(default=timezone.now)
    responsible = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Teammitglied'
        verbose_name_plural = 'Teammitglieder'
        unique_together = ['group', 'user']

    def __str__(self):
        return self.user.name


class CollectionGroupManager(models.Manager):
    def get_closest(self, geo):
        if not geo:
            return None
        groups = (
            self.get_queryset()
            .annotate(distance=Distance("geo", geo))
            .order_by("distance")
        )
        if groups:
            return groups[0]
        return None


class CollectionGroup(models.Model):
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    channel = models.CharField(max_length=255, blank=True)

    geo = models.PointField(null=True, blank=True, geography=True)

    members = models.ManyToManyField(User, through=CollectionGroupMember)

    calendar = models.ForeignKey(
        Calendar, null=True, blank=True, on_delete=models.SET_NULL
    )

    objects = CollectionGroupManager()

    class Meta:
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'

    def __str__(self):
        return 'Team {}'.format(self.name)

    def get_absolute_url(self):
        return reverse('collection:collectiongroup-detail', kwargs={'pk': self.pk})

    def get_domain_url(self):
        return settings.SITE_URL + self.get_absolute_url()

    def has_member(self, user):
        if not user.is_authenticated:
            return False
        return CollectionGroupMember.objects.filter(
                group=self, user=user).exists()


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

    def get_domain_url(self):
        return settings.SITE_URL + self.get_absolute_url()

    def get_domain_admin_url(self):
        return settings.SITE_URL + reverse('admin:collection_collectionlocation_change', args=(self.pk,))


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


class CollectionEventManager(models.Manager):
    pass


class CollectionEvent(models.Model):
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    geo = models.PointField(null=True, blank=True, geography=True)

    group = models.ForeignKey(
        CollectionGroup, null=True, blank=True,
        on_delete=models.SET_NULL
    )

    # FIXME: spelling
    event_occurence = models.ForeignKey(
        Occurrence, null=True, on_delete=models.CASCADE
    )
    members = models.ManyToManyField(User, through=CollectionEventMember)

    objects = CollectionEventManager()

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

    @property
    def start_time(self):
        tz = timezone.get_current_timezone()
        local_time = self.event_occurence.start.astimezone(tz)
        return date_format(local_time, "SHORT_DATETIME_FORMAT")

    @property
    def end_time(self):
        tz = timezone.get_current_timezone()
        local_time = self.event_occurence.end.astimezone(tz)
        return date_format(local_time, "SHORT_DATETIME_FORMAT")

    def get_absolute_url(self):
        return reverse('collection:collectionevent-join', kwargs={'pk': self.pk})

    def get_domain_url(self):
        return settings.SITE_URL + self.get_absolute_url()

    def get_non_attendees(self):
        if not self.group:
            return User.objects.none()
        return User.objects.filter(
            id__in=self.group.collectiongroupmember_set.exclude(
                user__in=self.members.all()
            ).values_list('user_id', flat=True)
        )


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
