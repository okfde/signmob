from datetime import timedelta

from django.db.models import Value, CharField, Q
from django.utils import timezone

from rest_framework_gis.serializers import (
    GeometryField, GeoFeatureModelListSerializer
)
from rest_framework import viewsets, serializers
from rest_framework.response import Response

from .models import CollectionGroup, CollectionLocation, CollectionEvent
from .utils import GeoJSONMixin


class CollectionSerializer(GeoJSONMixin, serializers.Serializer):
    """
    Combines CollectionGroup
    """

    id = serializers.SerializerMethodField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField()
    geometry = GeometryField(source='geo')
    kind = serializers.CharField()

    class Meta:
        list_serializer_class = GeoFeatureModelListSerializer

    def get_id(self, obj):
        return "{kind}_{id}".format(**obj)


class CollectionViewSet(viewsets.ViewSet):
    def list(self, request):
        columns = ("id", "name", "description", "geo", "kind")
        groups = (
            CollectionGroup.objects.all()
            .annotate(kind=Value("group", output_field=CharField()))
            .values(*columns)
        )
        events = (
            CollectionEvent.objects.all()
            .annotate(kind=Value("event", output_field=CharField()))
            .values(*columns)
        )
        locations = (
            CollectionLocation.objects.all()
            .annotate(kind=Value("location", output_field=CharField()))
            .values(*columns)
        )
        qs = groups.union(events).union(locations)
        serializer = CollectionSerializer(qs, many=True)
        return Response(serializer.data)
