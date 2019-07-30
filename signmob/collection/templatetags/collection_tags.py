from django import template

from ..forms import GroupSignupForm
from ..models import CollectionGroup, CollectionEvent

register = template.Library()


@register.simple_tag
def get_event_gantt_chart(event, event_members, user):
    return list(
        get_gantt_for_member(event, member, user)
        for member in event_members
    )


def get_gantt_for_member(event, member, user):
    duration = event.end - event.start

    offset = (member.start - event.start) / duration * 100

    member_duration = member.end - member.start
    width = member_duration / duration * 100

    return {
        'style': 'margin-left: {offset}%; width: {width}%'.format(
            offset=offset, width=width
        ),
        'member': member,
        'can_delete': member.user_id == user.id,
    }


@register.simple_tag
def get_signup_form():
    return GroupSignupForm()


@register.inclusion_tag('collection/_event_schedule.html')
def show_related_collection(event):
    calendar = event.calendar

    try:
        group = CollectionGroup.objects.get(calendar=calendar)
    except CollectionGroup.DoesNotExist:
        group = None

    events = CollectionEvent.objects.filter(
        event_occurence__event=event
    )

    return {
        'events': events,
        'group': group
    }
