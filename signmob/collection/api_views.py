from datetime import timedelta

from django.db.models import (
    F, Q, Value, CharField, IntegerField, DateTimeField
)
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format

from rest_framework_gis.serializers import (
    GeometryField, GeoFeatureModelListSerializer
)
from rest_framework import viewsets, serializers
from rest_framework.response import Response

from .models import CollectionGroup, CollectionLocation, CollectionEvent
from .utils import GeoJSONMixin


ACTION_URLS = {
    'group': 'collection:collectiongroup-detail',
    'location': 'collection:collectionlocation-report',
    'event': 'collection:collectionevent-join',
}


class CollectionSerializer(GeoJSONMixin, serializers.Serializer):
    """
    Combines CollectionGroup
    """

    id = serializers.SerializerMethodField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField()
    details = serializers.DictField()
    geometry = GeometryField(source='geo')
    kind = serializers.CharField()
    url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        list_serializer_class = GeoFeatureModelListSerializer

    def get_id(self, obj):
        return "{kind}_{id}".format(**obj)

    def get_url(self, obj):
        if obj['kind'] in ACTION_URLS:
            return settings.SITE_URL + reverse(
                ACTION_URLS[obj['kind']], kwargs={'pk': obj['id']}
            )
        return ''


def get_details(obj):
    if obj['kind'] == 'location':
        return {
            'address': obj['_address']
        }
    if obj['kind'] == 'event':
        tz = timezone.get_current_timezone()
        start = obj['_start'].astimezone(tz)
        start = date_format(start, "DATETIME_FORMAT")
        end = obj['_end'].astimezone(tz)
        end = date_format(end, "TIME_FORMAT")
        return {
            'group': obj['_group'],
            'start': obj['_start'],
            'end': obj['_end'],
            'start_format': start,
            'end_format': end,
        }
    return {}


def add_details(data):
    for d in data:
        d['details'] = get_details(d)
        yield d


class CollectionViewSet(viewsets.ViewSet):
    def list(self, request):
        # WARNING: only change order with care
        # https://code.djangoproject.com/ticket/28553
        columns = (
            "id", "name",
            "description", "geo",
            "_address",
            "_group",
            "_start",
            "_end",
            "kind",
        )

        groups = (
            CollectionGroup.objects.all()
            .annotate(
                _address=Value("", output_field=CharField()),
                _group=Value(None, output_field=IntegerField()),
                _start=Value(None, output_field=DateTimeField()),
                _end=Value(None, output_field=DateTimeField()),
                kind=Value("group", output_field=CharField()),
            )
            .values_list(*columns)
        )

        now = timezone.now()
        now_date = now.astimezone(timezone.get_current_timezone()).date()
        two_weeks = now + timedelta(days=15)
        events = (
            CollectionEvent.objects.filter(
                event_occurence__end__gte=now,
                event_occurence__start__lte=two_weeks,
            ).order_by('event_occurence__start')
            .annotate(
                _address=Value("", output_field=CharField()),
                _group=F('group_id'),
                _start=F('event_occurence__start'),
                _end=F('event_occurence__end'),
                kind=Value("event", output_field=CharField()),
            )
            .values_list(*columns)
        )
        locations = (
            CollectionLocation.objects.filter(
                (Q(end=None) | Q(end__gte=now_date))
                & Q(start__lte=now_date)
            )
            .annotate(
                _address=F('address'),
                _group=Value(None, output_field=IntegerField()),
                _start=Value(None, output_field=DateTimeField()),
                _end=Value(None, output_field=DateTimeField()),
                kind=Value("location", output_field=CharField())
            )
            .values_list(*columns)
        )
        qs = groups.union(events).union(locations)

        qs = list(add_details(dict(zip(columns, d)) for d in qs))

        serializer = CollectionSerializer(qs, many=True)
        return Response(serializer.data)
