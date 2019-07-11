from django.dispatch import Signal


group_joined = Signal(providing_args=["user", "group"])

location_created = Signal(providing_args=["location"])
location_reported = Signal(providing_args=["location"])

event_created = Signal(providing_args=["user", "group"])
