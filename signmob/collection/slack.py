import logging

import requests

from django.conf import settings

logger = logging.getLogger(__name__)


def send_message(message, group=None):
    logger.info('Sending slack message "%s" to %s', message, group)
    if not settings.SLACK_WEBHOOK_URL:
        return

    channel = settings.SLACK_DEFAULT_CHANNEL
    if group and group.channel:
        channel = group.channel

    requests.post(settings.SLACK_WEBHOOK_URL, json={
        'channel': channel,
        'username': 'orga-bot',
        'text': message,
        'icon_emoji': ':robot_face:'
    })


SLACK_INVITE_URL = 'https://slack.com/api/users.admin.invite'


def invite_email(email):
    logger.info('Inviting email %s', email)
    if not settings.SLACK_LEGACY_TOKEN:
        return

    requests.post(SLACK_INVITE_URL, data={
        'token': settings.SLACK_LEGACY_TOKEN,
        'email': email,
        'channels': settings.SLACK_INVITE_CHANNELS,
        'restricted': 'true'
    })
