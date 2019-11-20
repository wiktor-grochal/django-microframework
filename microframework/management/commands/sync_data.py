from importlib import import_module
from nameko.standalone.events import event_dispatcher
import logging
import pytz
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core import serializers
from microframework.utils import sort_models_by_relations
from microframework.sender import DateTimeDecimalEncoder

log = logging.getLogger(__name__)
encoder = DateTimeDecimalEncoder()


class Command(BaseCommand):
    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('models', type=str, nargs='+',
                            help='List of models to sync')

    def handle(self, *args, **options):
        if not hasattr(settings, 'MICROFRAMEWORK_AMQP_URI'):
            log.error('You need to define MICROFRAMEWORK_AMQP_URI in django settings')
            return False
        if not hasattr(settings, 'MICROFRAMEWORK_SENDER_NAME'):
            log.error('You need to define MICROFRAMEWORK_SENDER_NAME in django settings')
            return False
        amqp_config = {
            'AMQP_URI': settings.MICROFRAMEWORK_AMQP_URI
        }

        dispatch = event_dispatcher(amqp_config)
        unsorted_models = []
        for model_name in options['models']:
            model_splitted = model_name.rsplit('.', 1)
            module = model_splitted[0]
            cls = model_splitted[1]
            model = getattr(import_module(module), cls)
            unsorted_models.append(model)
        sorted_models = sort_models_by_relations(unsorted_models)

        for model in sorted_models:
            for instance in model.objects.all():
                object_data = serializers.serialize("python", [instance, ])[0]
                payload = {
                    'sync_data': {
                        'models_list': [],
                        'date_modified': datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
                    },
                    'object_data': object_data
                }
                payload = encoder.encode(payload)
                dispatch(settings.MICROFRAMEWORK_SENDER_NAME, f'{model.__name__}_saved', payload)
