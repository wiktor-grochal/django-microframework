from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import RegularModel, JSONModel, ForeignKeyModel, TreeModel, SecondForeignKeyModel

admin.site.register(RegularModel)
admin.site.register(JSONModel)
admin.site.register(ForeignKeyModel)
admin.site.register(SecondForeignKeyModel)


@admin.register(TreeModel)
class AccountAdmin(MPTTModelAdmin):
    model = TreeModel
