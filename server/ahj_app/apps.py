from django.contrib.admin.apps import AdminConfig
from django.apps import AppConfig
from django.conf import settings
import os


class AhjAdminConfig(AdminConfig):
    """
    Custom admin config to point Django to the custom admin site.
    """
    default_site = 'ahj_app.admin.admin.AHJRegistryAdminSite'


class AhjConfig(AppConfig):
    name = 'ahj_app'
    verbose_name = 'AHJ Registry'
    def ready(self) -> None:
        # Start the updater for db procedures
        from ScheduledTasks import updater
        updater.start()



