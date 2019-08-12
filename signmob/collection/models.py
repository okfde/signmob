from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from schedule.models import Calendar, Occurrence, Event

from signmob.users.models import User


def new_occurrence_hash(self):
    # monkey patch for Unhashable Type Occurrence
    return hash((self.event_id, self.original_start, self.original_end))


Occurrence.__hash__ = new_occurrence_hash


class CollectionGroupMember(models.Model):
    group = models.ForeignKey("CollectionGroup", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, verbose_name=_('user'),
        on_delete=models.CASCADE)
    joined = models.DateTimeField(_('joined'), default=timezone.now)
    responsible = models.BooleanField(_('responsible'), default=False)

    class Meta:
        verbose_name = _('team member')
        verbose_name_plural = _('team members')
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
    name = models.CharField(_('name'), max_length=255, blank=True)
    description = models.TextField(_('description'), blank=True)
    channel = models.CharField(_('channel'), max_length=255, blank=True)

    geo = models.PointField(_('place'), null=True, blank=True, geography=True)

    members = models.ManyToManyField(
        User, through=CollectionGroupMember,
        verbose_name=_('members')
    )

    calendar = models.ForeignKey(
        Calendar, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_('calendar')
    )

    objects = CollectionGroupManager()

    class Meta:
        verbose_name = _('team')
        verbose_name_plural = _('teams')

    def __str__(self):
        return _('Team {}').format(self.name)

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
    name = models.CharField(_('name'), max_length=255, blank=True)
    description = models.TextField(_('description'), blank=True)

    address = models.TextField(_('address'), blank=True)
    geo = models.PointField(_('place'), null=True, blank=True, geography=True)

    start = models.DateField(_('start'), null=True, blank=True)
    end = models.DateField(_('end'), null=True, blank=True)

    accumulation = models.BooleanField(_('accumulation'), default=False)

    events = models.ManyToManyField(
        Event, blank=True,
        verbose_name=_('opening hours'))
    email = models.EmailField(_('email'), blank=True)
    user = models.ForeignKey(
        User, blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('user')
    )
    needs_check = models.BooleanField(_('needs check'), default=False)
    send_material = models.BooleanField(_('send material'), default=False)
    report = models.TextField(_('report'), blank=True)

    class Meta:
        verbose_name = _('collection place')
        verbose_name_plural = _('collection places')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('collection:collectionlocation-report', kwargs={'pk': self.pk})

    def get_domain_url(self):
        return settings.SITE_URL + self.get_absolute_url()

    def get_domain_admin_url(self):
        return settings.SITE_URL + reverse('admin:collection_collectionlocation_change', args=(self.pk,))


class CollectionEventMember(models.Model):
    event = models.ForeignKey(
        "CollectionEvent", on_delete=models.CASCADE,
        verbose_name=_('collection event')
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name=_('user')
    )

    start = models.DateTimeField(_('start'), null=True, blank=True)
    end = models.DateTimeField(_('end'), null=True, blank=True)

    note = models.TextField(_('note'), blank=True)

    class Meta:
        verbose_name = _('collection event member')
        verbose_name_plural = _('collection event member')
        ordering = ('start', '-end')

    def __str__(self):
        return _('{} at {}').format(self.user, self.event)


class CollectionEventManager(models.Manager):
    pass


class CollectionEvent(models.Model):
    name = models.CharField(_('name'), max_length=255, blank=True)
    description = models.TextField(_('description'), blank=True)

    geo = models.PointField(_('place'), null=True, blank=True, geography=True)

    group = models.ForeignKey(
        CollectionGroup, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('group')
    )

    # FIXME: spelling
    event_occurence = models.ForeignKey(
        Occurrence, null=True, on_delete=models.CASCADE,
        verbose_name=_('event')
    )
    members = models.ManyToManyField(
        User, through=CollectionEventMember,
        verbose_name=_('members')
    )

    objects = CollectionEventManager()

    class Meta:
        verbose_name = _('collection event')
        verbose_name_plural = _('collection events')
        ordering = ('-event_occurence__start',)

    def __str__(self):
        if not self.event_occurence:
            return self.name
        return _('{date} - {end}: {name}').format(
            date=date_format(self.start, "SHORT_DATETIME_FORMAT"),
            end=date_format(self.end, "TIME_FORMAT"),
            name=self.name
        )

    @property
    def start(self):
        if self.event_occurence:
            return self.event_occurence.start

    @property
    def end(self):
        if self.event_occurence:
            return self.event_occurence.end

    @property
    def start_time(self):
        if self.event_occurence:
            tz = timezone.get_current_timezone()
            local_time = self.event_occurence.start.astimezone(tz)
            return date_format(local_time, "SHORT_DATETIME_FORMAT")

    @property
    def end_time(self):
        if self.event_occurence:
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
    amount = models.IntegerField(_('amount'), default=0)

    start = models.DateTimeField(_('start'), null=True, blank=True)
    end = models.DateTimeField(_('end'), null=True, blank=True)

    comment = models.TextField(_('comment'), blank=True)

    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name=_('user')
    )

    group = models.ForeignKey(
        CollectionGroup, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_('team')
    )
    location = models.ForeignKey(
        CollectionLocation, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_('collection location')
    )
    event = models.ForeignKey(
        CollectionEvent, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_('collection event')
    )

    class Meta:
        verbose_name = _('collection result')
        verbose_name_plural = _('collection results')

    def __str__(self):
        return '{} ({} - {})'.format(self.amount, self.start, self.end)
