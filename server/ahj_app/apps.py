from django.apps import AppConfig
from django.conf import settings
import os


class AhjConfig(AppConfig):
    name = 'ahj_app'
    def ready(self) -> None:
        # Start the updater for db procedures
        from ScheduledTasks import updater
        updater.start()



