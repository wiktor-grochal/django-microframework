from decimal import Decimal
from nameko.standalone.events import event_dispatcher
from django.db.models.signals import post_save, post_delete
import pytz
from django.core import serializers
import json
import datetime
import logging
from django.conf import settings
from .utils import create_model_name_list

log = logging.getLogger(__name__)

if not hasattr(settings, 'MICROFRAMEWORK_AMQP_URI'):
    raise Exception('You need to define MICROFRAMEWORK_AMQP_URI in django settings')

AMQP_CONFIG = {
    'AMQP_URI': settings.MICROFRAMEWORK_AMQP_URI
}

dispatch = event_dispatcher(AMQP_CONFIG)


class DateTimeDecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        elif isinstance(obj, Decimal):
            return str(obj)
        return super(DateTimeDecimalEncoder, self).default(obj)


encoder = DateTimeDecimalEncoder()


def create_save_signal_handler(synced_save_model, sender_name, model_name_list):
    def handler(sender, instance, created, **kwargs):
        object_data = serializers.serialize("python", [instance, ])[0]
        payload = {
            'sync_data': {
                'models_list': model_name_list,
                'date_modified': datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            },
            'object_data': object_data
        }
        payload = encoder.encode(payload)
        dispatch(sender_name, f'{synced_save_model.__name__}_saved', payload)
    return handler


def create_delete_signal_handler(synced_save_model, sender_name, model_name_list):
    def handler(sender, instance, **kwargs):
        object_data = serializers.serialize("python", [instance, ])[0]
        payload = {
            'sync_data': {
                'models_list': model_name_list
            },
            'object_data': object_data
        }
        payload = encoder.encode(payload)
        dispatch(sender_name, f'{synced_save_model.__name__}_deleted', payload)
    return handler


def connect_signals(models, sender_name=None):
    if not sender_name:
        if not hasattr(settings, 'MICROFRAMEWORK_SENDER_NAME'):
            raise Exception('You need to define MICROFRAMEWORK_SENDER_NAME in django settings')
        sender_name = settings.MICROFRAMEWORK_SENDER_NAME

    model_name_list = create_model_name_list(models)
    for synced_save_model in models:
        save_signal_handler = create_save_signal_handler(synced_save_model, sender_name, model_name_list)
        delete_signal_handler = create_delete_signal_handler(synced_save_model, sender_name, model_name_list)
        post_save.connect(save_signal_handler, sender=synced_save_model, weak=False)
        post_delete.connect(delete_signal_handler, sender=synced_save_model, weak=False)
