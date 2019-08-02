from datetime import timedelta

from django.utils import formats
from django.utils import timezone

from config.celery_app import app as celery_app

from signmob.users.models import User
from signmob.users.utils import send_template_email

from .models import CollectionEvent, CollectionGroup, CollectionLocation
from .slack import send_message


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


@celery_app.task
def event_created_task(user_id, event_id):
    try:
        event = CollectionEvent.objects.get(id=event_id)
    except CollectionGroup.DoesNotExist:
        return

    message_event_created(event)


def message_event_created(event):
    if event.group:
        message = 'Team {team} hat den nächsten Sammeltermin: <{url}|{date}>'.format(
            team=event.group.name, url=event.get_domain_url(),
            date=formats.date_format(event.start, 'SHORT_DATE_FORMAT')
        )
        send_message(message, group=event.group)

    else:
        message = 'Team {team} hat den nächsten Sammeltermin: <{url}|{date}>'.format(
            team=event.group.name, url=event.get_domain_url(),
            date=formats.date_format(event.start, 'SHORT_DATE_FORMAT')
        )
        send_message(message, group=event.group)

    if event.group:
        subject = 'Team {name} hat eine neuen Sammeltermin: {date}'.format(
            name=event.group.name,
            date=formats.date_format(event.start, 'SHORT_DATE_FORMAT')
        )
        users = event.group.members.all()
    else:
        subject = 'Neuer Sammeltermin: {date}'.format(
            date=formats.date_format(event.start, 'SHORT_DATE_FORMAT')
        )
        users = User.objects.all()

    for user in users:
        send_template_email(
            user=user,
            subject=subject,
            template='collection/emails/event_created.txt',
            context={
                'user': user,
                'event': event
            }
        )


INTERVAL_HOURS = 1


@celery_app.task
def event_checker():
    now = timezone.now()
    start = now + timedelta(days=1)
    end = start + timedelta(hours=INTERVAL_HOURS)
    # start tomorrow within one hour window
    events = CollectionEvent.objects.filter(
        event_occurence__start__gte=start,
        event_occurence__start__lt=end,
    )
    for event in events:
        announce_event_tomorrow(event)


def announce_event_tomorrow(event):
    if event.group:
        send_message('Morgen sammelt das Team {team}! <{url}|Hier ist das Event>'.format(
            team=event.group.name,
            url=event.get_domain_url()
        ))
    else:
        send_message('Morgen findet das allgemeine Sammelevent "{name}" statt! <{url}|Hier zum Mitsammeln eintragen!>'.format(
            name=event.name,
            url=event.get_domain_url()
        ))

    for member in event.collectioneventmember_set.all():
        send_template_email(
            user=member.user,
            subject='Morgen sammeln für den Volksentscheid Transparenz',
            template='collection/emails/event_tomorrow.txt',
            context={
                'user': member.user,
                'event': event
            }
        )

    if event.group:
        users = event.get_non_attendees()

        for user in users:
            send_template_email(
                user=user,
                subject='Spontan Zeit für den Volksentscheid Transparenz?',
                template='collection/emails/event_tomorrow_missing.txt',
                context={
                    'user': user,
                    'event': event,
                    'team': event.group
                }
            )
