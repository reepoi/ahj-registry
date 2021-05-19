from django.apps import AppConfig
from django.conf import settings
import os


class AhjConfig(AppConfig):
    name = 'ahj_app'
    def ready(self) -> None:
        # Create media_root dir
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        # Create additional dirs if they don't exist
        for dir in settings.STORAGE_DIRS.values():
            if not os.path.exists(settings.MEDIA_ROOT + dir):
                os.makedirs(settings.MEDIA_ROOT + dir)
        # Start the updater for db procedures
        from ScheduledTasks import updater
        updater.start()



