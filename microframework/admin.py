from django.contrib import admin
from .models import SyncData, PendingObjects

admin.site.register(SyncData)
admin.site.register(PendingObjects)
