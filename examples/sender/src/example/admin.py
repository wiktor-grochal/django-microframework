from django.contrib import admin
# from mptt.admin import MPTTModelAdmin
from .models import RegularModel


admin.site.register(RegularModel)

