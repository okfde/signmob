from collections import OrderedDict

from django.conf import settings
from django.utils import timezone

from schedule.periods import Month


class GeoJSONMixin(object):
    def to_representation(self, instance):
        """
        Serialize objects -> primitives.
        """
        # prepare OrderedDict geojson structure
        feature = OrderedDict()
        # the list of fields that will be processed by get_properties
        # we will remove fields that have been already processed
        # to increase performance on large numbers
        fields = list(self.fields.values())

        field = self.fields['id']
        value = field.get_attribute(instance)
        feature["id"] = field.to_representation(value)
        fields.remove(field)

        # required type attribute
        # must be "Feature" according to GeoJSON spec
        feature["type"] = "Feature"

        # required geometry attribute
        # MUST be present in output according to GeoJSON spec
        field = self.fields['geometry']
        geo_value = field.get_attribute(instance)
        feature["geometry"] = field.to_representation(geo_value)
        fields.remove(field)

        # GeoJSON properties
        feature["properties"] = self.get_properties(instance, fields)

        return feature

    def get_properties(self, instance, fields):
        """
        Get the feature metadata which will be used for the GeoJSON
        "properties" key.
        By default it returns all serializer fields excluding those used for
        the ID, the geometry and the bounding box.
        :param instance: The current Django model instance
        :param fields: The list of fields to process (fields already processed have been removed)
        :return: OrderedDict containing the properties of the current feature
        :rtype: OrderedDict
        """
        properties = OrderedDict()

        for field in fields:
            if field.write_only:
                continue
            value = field.get_attribute(instance)
            representation = None
            if value is not None:
                representation = field.to_representation(value)
            properties[field.field_name] = representation

        return properties


def get_period(calendar, period_class=Month):
        event_list = settings.GET_EVENTS_FUNC(None, calendar)
        date = timezone.now()
        local_timezone = timezone.get_current_timezone()
        return period_class(event_list, date, tzinfo=local_timezone)
