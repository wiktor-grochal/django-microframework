from django.apps import AppConfig


class ExampleConfig(AppConfig):
    name = 'example'

    def ready(self):
        from django.conf import settings
        if settings.PUBLISH_EVENTS:
            import example.events
