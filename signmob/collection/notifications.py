from django.dispatch import receiver
from django.db.models import signals

from .signals import (
    group_joined, location_created, location_reported,
    event_created,
)
from .models import CollectionEvent
from .tasks import (
    location_created_task, location_reported_task,
    group_joined_task,
    event_created_task
)


@receiver(signals.post_save, sender=CollectionEvent)
def trigger_event_created(sender, instance=None, created=False, **kwargs):
    if kwargs.get('raw'):
        return
    if not created:
        return
    event_created.send(sender=CollectionEvent, event=instance)


@receiver(location_created)
def notify_location_created(sender, location, **kwargs):
    location_created_task.delay(location.id)


@receiver(location_reported)
def notify_location_reported(sender, location, **kwargs):
    location_reported_task.delay(location.id)


@receiver(group_joined)
def notify_group_joined(sender, user, group, **kwargs):
    group_joined_task.delay(user.id, group.id)


@receiver(event_created)
def notify_event_created(sender, event, **kwargs):
    event_created_task.delay(event.id)
