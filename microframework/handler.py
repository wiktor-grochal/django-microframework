import json
import logging
from dateutil.parser import parse
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.utils import IntegrityError
from django.conf import settings
from nameko.events import BROADCAST, EventHandler
from .const import RELATIONAL_FIELDS
from .utils import create_model_name_list, transform_serialized_foreign_fields
from .models import SyncData, PendingObjects


log = logging.getLogger(__name__)
log.setLevel(getattr(settings, 'DJANGO_LOG_LEVEL', 'INFO'))


class HandlerException(Exception):
    pass


class DjangoObjectHandler:
    synced_save_models = []

    @staticmethod
    def save_object(data, model):
        fields = data["object_data"]["fields"]
        fields_transformed = transform_serialized_foreign_fields(fields, model)
        sync_data, created = SyncData.objects.get_or_create(
            object_id=data["object_data"]["pk"],
            content_type=ContentType.objects.get_for_model(model),
            defaults={'date_modified': data["sync_data"]["date_modified"]}
        )
        if not created:
            if sync_data.date_modified > parse(data["sync_data"]["date_modified"]):
                log.warning("Sync data mismatch. Incoming object is older "
                            "than current object in database")
                return False
        model.objects.update_or_create(
            pk=data["object_data"]["pk"],
            defaults=fields_transformed
        )
        sync_data.date_modified = data["sync_data"]["date_modified"]
        sync_data.save()
        log.info(f'{model.__name__} pk:{data["object_data"]["pk"]} saved')

    @classmethod
    def save_pending_objects(cls, data, model):
        pending_objects = PendingObjects.objects.filter(
            object_id=data["object_data"]["pk"],
            content_type=ContentType.objects.get_for_model(model)
        )
        saved = 0
        for pending_object in pending_objects:
            pending_data = json.loads(pending_object.object_serialized)
            model = pending_object.content_type.model_class()
            cls.save_object(pending_data, model)
            pending_object.delete()
            saved += 1
        if saved:
            log.info(f'{saved} PendingObjects saved')

    @staticmethod
    def create_pending_objects(data, model):
        model_fields = model._meta.get_fields()
        payload = json.dumps(data)
        created = 0
        for model_field in model_fields:
            if model_field.__class__.__name__ in RELATIONAL_FIELDS:
                object_id = data["object_data"]["fields"][model_field.name]
                content_type = ContentType.objects.get_for_model(
                    model_field.related_model
                )
                PendingObjects.objects.create(
                    object_id=object_id,
                    content_type=content_type,
                    object_serialized=payload
                )
                created += 1
        if created:
            log.info(f'{created} PendingObjects created')

    @classmethod
    def verify_sync(cls, data):
        sync_data = data['sync_data']
        sender_models_list = sync_data['models_list']
        listener_models_list = create_model_name_list(cls.synced_save_models)
        if not set(sender_models_list) == set(listener_models_list):
            log.warning(f"Sender and listener models list are not the same. "
                        f"Sender:{str(sender_models_list)} "
                        f"Listener: {str(listener_models_list)}")

    @classmethod
    def object_saved_handler(cls, payload, model):
        log.debug(f'Incoming data: {payload}')
        data = json.loads(payload)
        cls.verify_sync(data)
        try:
            with transaction.atomic():
                cls.save_object(data, model)
                cls.save_pending_objects(data, model)
        except IntegrityError:
            cls.create_pending_objects(data, model)

    @classmethod
    def object_deleted_handler(cls, payload, model):
        log.debug(f'Incoming data: {payload}')
        data = json.loads(payload)
        cls.verify_sync(data)
        with transaction.atomic():
            obj = model.objects.get(pk=data["object_data"]["pk"])
            obj.delete()
            pending_objects = PendingObjects.objects.filter(
                object_id=data["object_data"]["pk"],
                content_type=ContentType.objects.get_for_model(model)
            )
            for pending_object in pending_objects:
                pending_object.delete()
        log.info(f'{model.__name__} pk:{data["object_data"]["pk"]} deleted')


class NamekoHandlerMeta(type):
    def __new__(mcs, name, bases, dct):
        x = super().__new__(mcs, name, bases, dct)
        try:
            sender_name = dct['sender_name']
        except KeyError:
            raise HandlerException('Service class must define a `sender_name` attribute')
        try:
            synced_save_models = dct['synced_save_models']
        except KeyError:
            raise HandlerException('Service class must define a `synced_save_models` attribute')
        try:
            service_name = dct['name']
        except KeyError:
            raise HandlerException('Service class must define a `name` attribute')

        class BroadcastEventHandler(EventHandler):
            broadcast_identifier = service_name

        event_handler = BroadcastEventHandler.decorator

        for synced_save_model in synced_save_models:
            saved_method_name = f'{synced_save_model.__name__}_saved'
            deleted_method_name = f'{synced_save_model.__name__}_deleted'
            setattr(
                x,
                saved_method_name,
                mcs.create_saved_nameko_handler(
                    sender_name,
                    synced_save_model,
                    event_handler))
            setattr(
                x,
                deleted_method_name,
                mcs.create_deleted_nameko_handler(
                    sender_name,
                    synced_save_model,
                    event_handler))
        return x

    @classmethod
    def create_saved_nameko_handler(mcs, sender_name, model, event_handler):
        @event_handler(sender_name,
                       f'{model.__name__}_saved',
                       handler_type=BROADCAST,
                       requeue_on_error=True)
        def handler(self, payload):
            self.object_saved_handler(payload, model)
        return handler

    @classmethod
    def create_deleted_nameko_handler(mcs, sender_name, model, event_handler):
        @event_handler(sender_name,
                       f'{model.__name__}_deleted',
                       handler_type=BROADCAST,
                       requeue_on_error=True)
        def handler(self, payload):
            self.object_deleted_handler(payload, model)
        return handler
