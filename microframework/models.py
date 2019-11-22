import logging
import json
from django.db import models
from dateutil.parser import parse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

log = logging.getLogger(__name__)


class SyncData(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    date_modified = models.DateTimeField()


class PendingObjects(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object_serialized = models.TextField()

    def get_field_by_name(self, name, model_meta_fields):
        for field in model_meta_fields:
            if field.name == name:
                return field
        return None

    def save_object(self):
        data = json.loads(self.object_serialized)
        model = self.content_type.model_class()
        # content_type = ContentType.objects.get(id=self.content_type.model_class())
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
        sync_data, created = SyncData.objects.get_or_create(object_id=data["object_data"]["pk"],
                                                            content_type=ContentType.objects.get_for_model(model),
                                                            defaults={'date_modified': data["sync_data"]["date_modified"]})
        if not created:
            if sync_data.date_modified > parse(data["sync_data"]["date_modified"]):
                log.warning("Sync data mismatch. Incoming object is older than current object in database")
                return False
        model.objects.update_or_create(id=data["object_data"]["pk"],
                                       defaults=fields_trimmed)
        sync_data.date_modified = data["sync_data"]["date_modified"]
        sync_data.save()
        self.delete()


