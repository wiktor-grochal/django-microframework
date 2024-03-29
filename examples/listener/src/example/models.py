from django.contrib.postgres.fields import JSONField
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
import uuid


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

    def __str__(self):
        return self.char


class JSONModel(models.Model):
    json = JSONField()

    def __str__(self):
        return repr(self.json)


class TreeModel(MPTTModel):
    name = models.CharField(max_length=255, null=True)
    parent_name = models.CharField(max_length=255, null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name


class ForeignKeyModel(models.Model):
    foreign_key = models.ForeignKey(RegularModel, on_delete=models.CASCADE)
    tree = TreeForeignKey(TreeModel, on_delete=models.CASCADE)

    def __str__(self):
        return f'{str(self.foreign_key)}:{str(self.tree)}'


class SecondForeignKeyModel(models.Model):
    foreign_key_2 = models.ForeignKey(ForeignKeyModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name


class UuidAsIdModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name
