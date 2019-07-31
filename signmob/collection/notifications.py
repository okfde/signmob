from django.dispatch import receiver

from .signals import (
    group_joined, location_created, location_reported,
    event_created,
    event_in_week, event_tomorrow, event_finished
)
from .tasks import (
    location_created_task, location_reported_task,
    group_joined_task
)


@receiver(location_created)
def notify_location_created(sender, location, **kwargs):
    location_created_task.delay(location.id)


@receiver(location_reported)
def notify_location_reported(sender, location, **kwargs):
    location_reported_task.delay(location.id)


@receiver(group_joined)
def notify_group_joined(sender, user, group, **kwargs):
    group_joined_task.delay(user.id, group.id)