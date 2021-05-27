from django.contrib.admin.apps import AdminConfig
from django.apps import AppConfig


class AhjAdminConfig(AdminConfig):
    default_site = 'ahj_app.admin.AHJRegistryAdminSite'


class AhjConfig(AppConfig):
    name = 'ahj_app'
    verbose_name = 'AHJ Registry'
    def ready(self) -> None:
        # Start the updater for db procedures
        from ScheduledTasks import updater
        updater.start()

