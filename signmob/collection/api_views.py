from django.db.models import Value, CharField
from django.conf import settings
from django.urls import reverse


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


class CollectionViewSet(viewsets.ViewSet):
    def list(self, request):
        columns = ("id", "name", "description", "geo", "kind")

        # non_group_events = CollectionEvent.objects.filter(group=None)
        groups = (
            CollectionGroup.objects.all()
            .annotate(
                kind=Value("group", output_field=CharField()),
            )
            .values(*columns)
        )
        events = (
            CollectionEvent.objects.all()
            .annotate(
                kind=Value("event", output_field=CharField())
            )
            .values(*columns)
        )
        locations = (
            CollectionLocation.objects.all()
            .annotate(
                kind=Value("location", output_field=CharField())
            )
            .values(*columns)
        )
        qs = groups.union(events).union(locations)
        serializer = CollectionSerializer(qs, many=True)
        return Response(serializer.data)
