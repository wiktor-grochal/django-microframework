# from django.contrib.postgres.fields import JSONField
from django.db import models
# from mptt.models import MPTTModel, TreeForeignKey
from .events import connect_signals


class RegularModel(models.Model):
    big_int = models.BigIntegerField(null=True)
    binary = models.BinaryField(null=True)
    bool = models.BooleanField(null=True)
    char = models.CharField(max_length=255, null=True)
    date = models.DateField(null=True)
    datetime = models.DateTimeField(null=True)
    decimal = models.DecimalField(decimal_places=10, max_digits=15, null=True)
    duration = models.DurationField(null=True)
    email = models.EmailField(null=True)
    float = models.FloatField(null=True)
    int = models.IntegerField(null=True)
    ip = models.GenericIPAddressField(null=True)
    null_bool = models.NullBooleanField(null=True)
    positive_int = models.PositiveIntegerField(null=True)
    positive_small_int = models.PositiveSmallIntegerField(null=True)
    slug = models.SlugField(null=True)
    small_int = models.SmallIntegerField(null=True)
    text = models.TextField(null=True)
    time = models.TimeField(null=True)
    url = models.URLField(null=True)
    uuid = models.UUIDField(null=True)


connect_signals([RegularModel], 'example_sender')
