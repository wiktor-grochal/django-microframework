from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import RegularModel, JSONModel, ForeignKeyModel, TreeModel, SecondForeignKeyModel, \
    UuidAsIdModel



admin.site.register(RegularModel)
admin.site.register(JSONModel)
admin.site.register(ForeignKeyModel)
admin.site.register(SecondForeignKeyModel)
admin.site.register(UuidAsIdModel)


@admin.register(TreeModel)
class TreeAdmin(MPTTModelAdmin):
    model = TreeModel
