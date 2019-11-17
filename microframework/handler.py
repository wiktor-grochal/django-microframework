from nameko.events import event_handler
from .utils import create_model_name_list
import json
import logging


log = logging.getLogger(__name__)


class HandlerException(Exception):
    pass


class DjangoObjectHandler:
    synced_save_models = []

    def get_field_by_name(self, name, model_meta_fields):
        for field in model_meta_fields:
            if field.name == name:
                return field
        return None

    def verify_sync(self, sync_data):
        sender_models_list = sync_data['models_list']
        listener_models_list = create_model_name_list(self.synced_save_models)
        if not set(sender_models_list) == set(listener_models_list):
            log.warning(f"Sender and listener models list are not the same. "
                        f"Sender:{str(sender_models_list)} Listener: {str(listener_models_list)}")

    def object_saved_handler(self, payload, model):
        data = json.loads(payload)
        self.verify_sync(data["sync_data"])
        fields = data["object_data"]["fields"]
        fields_trimmed = {}

        for field_name, field_value in fields.items():
            field = self.get_field_by_name(field_name, model._meta.fields)
            if field:
                field_type = field.get_internal_type()
                if field_type in ['ForeignKey', 'TreeForeignKey']:
                    fields_trimmed[f'{field_name}_id'] = field_value
                else:
                    fields_trimmed[field_name] = field_value

        obj, created = model.objects.update_or_create(id=data["object_data"]["pk"],
                                                      defaults=fields_trimmed)

    def object_deleted_handler(self, payload, model):
        data = json.loads(payload)
        obj = model.objects.get(id=data["object_data"]["pk"])
        obj.delete()


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
        for synced_save_model in synced_save_models:
            saved_method_name = f'{synced_save_model.__name__}_saved'
            deleted_method_name = f'{synced_save_model.__name__}_deleted'
            setattr(x, saved_method_name, mcs.create_saved_nameko_handler(sender_name, synced_save_model))
            setattr(x, deleted_method_name, mcs.create_deleted_nameko_handler(sender_name, synced_save_model))
        return x

    @classmethod
    def create_saved_nameko_handler(mcs, sender_name, model):
        @event_handler(sender_name, f'{model.__name__}_saved')
        def handler(self, payload):
            self.object_saved_handler(payload, model)
            log.info(f'{model.__name__}_saved')
        return handler

    @classmethod
    def create_deleted_nameko_handler(mcs, sender_name, model):
        @event_handler(sender_name, f'{model.__name__}_deleted')
        def handler(self, payload):
            self.object_deleted_handler(payload, model)
            log.info(f'{model.__name__}_deleted')
        return handler
