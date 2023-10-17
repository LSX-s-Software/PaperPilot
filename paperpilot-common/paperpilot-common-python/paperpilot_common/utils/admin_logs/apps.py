"""
Django Admin Logs - App Config.
"""
from django.apps import AppConfig
from django.db import models


class DjangoAdminLogsConfig(AppConfig):
    name = "paperpilot_common.utils.admin_logs"
    verbose_name = "Django Admin Logs"

    def ready(self):
        from django.contrib.admin.models import LogEntry

        from .models import NoUserEntryManager

        # Change the model manager to one that doesn't log user
        LogEntry.objects = NoUserEntryManager(LogEntry)

        from django.contrib.admin.templatetags.log import AdminLogNode

        from .render import custom_render

        AdminLogNode.render = custom_render

        from django.contrib.admin.models import LogEntry

        LogEntry.user = None
        LogEntry.user_id = models.IntegerField(default=0, verbose_name="user")
