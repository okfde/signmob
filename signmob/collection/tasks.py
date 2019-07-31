from django.conf import settings
from django.utils import translation

from config.celery_app import app as celery_app

from signmob.users.models import User

from .models import CollectionGroup, CollectionLocation
from .slack import send_message


@celery_app.task
def event_over_task():
    translation.activate(settings.LANGUAGE_CODE)


@celery_app.task
def location_created_task(location_id):
    try:
        location = CollectionLocation.objects.get(id=location_id)
    except CollectionLocation.DoesNotExist:
        return

    group = CollectionGroup.objects.get_closest(location.geo)

    message = 'Yeah ein neuer Sammelort wurde angelegt: "<{url}|{name}">!'.format(
        name=location.name, url=location.get_domain_admin_url()
    )
    if group:
        message += ' Das Team {team} ist am nächsten.'.format(
            team=group.name
        )
    send_message(message, group=group)


@celery_app.task
def location_reported_task(location_id):
    try:
        location = CollectionLocation.objects.get(id=location_id)
    except CollectionLocation.DoesNotExist:
        return

    group = CollectionGroup.objects.get_closest(location.geo)

    message = 'Oh oh, Problem beim Sammelort "<{url}|{name}"> gemeldet.'.format(
        name=location.name, url=location.get_domain_admin_url()
    )
    if group:
        message += ' Das Team {team} ist am nächsten.'.format(
            team=group.name
        )
    send_message(message, group=group)


@celery_app.task
def group_joined_task(user_id, group_id):
    try:
        group = CollectionGroup.objects.get(id=group_id)
    except CollectionGroup.DoesNotExist:
        return
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    message = 'Hurra! Team {team} hat ein neues Mitglied: {name}'.format(
        team=group.name, name=user.name
    )
    send_message(message, group=group)
