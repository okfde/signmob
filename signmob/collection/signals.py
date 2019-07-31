from django.dispatch import Signal


group_joined = Signal(providing_args=["user", "group"])

location_created = Signal(providing_args=["location"])
location_reported = Signal(providing_args=["location"])

event_created = Signal(providing_args=["user", "event"])
event_in_week = Signal(providing_args=["event"])
event_tomorrow = Signal(providing_args=["event"])
event_finished = Signal(providing_args=["event"])
