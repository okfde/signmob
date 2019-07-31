from django.apps import AppConfig


class CollectionConfig(AppConfig):
    name = "signmob.collection"
    verbose_name = 'Unterschriften sammeln'

    def ready(self):
        # setup signal listeners
        from . import notifications # noqa
