from decimal import Decimal
from nameko.standalone.events import event_dispatcher
from django.db.models.signals import post_save, post_delete
from django.core import serializers
import json
import datetime

AMQP_URI = 'pyamqp://guest:guest@172.17.0.5'
AMQP_CONFIG = {
    'AMQP_URI': AMQP_URI
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


def create_save_signal_handler(synced_save_model, sender_name):
    def handler(sender, instance, created, **kwargs):
        payload = serializers.serialize("python", [instance, ])[0]
        payload = encoder.encode(payload)
        dispatch(sender_name, f'{synced_save_model.__name__}_saved', payload)
    return handler


def create_delete_signal_handler(synced_save_model, sender_name):
    def handler(sender, instance, **kwargs):
        payload = serializers.serialize("python", [instance, ])[0]
        payload = encoder.encode(payload)
        dispatch(sender_name, f'{synced_save_model.__name__}_deleted', payload)
    return handler


def connect_signals(models, sender_name):
    for synced_save_model in models:
        save_signal_handler = create_save_signal_handler(synced_save_model, sender_name)
        delete_signal_handler = create_delete_signal_handler(synced_save_model, sender_name)
        post_save.connect(save_signal_handler, sender=synced_save_model, weak=False)
        post_delete.connect(delete_signal_handler, sender=synced_save_model, weak=False)
