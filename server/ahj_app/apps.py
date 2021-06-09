from django.apps import AppConfig


class AhjConfig(AppConfig):
    name = 'ahj_app'
    def ready(self) -> None:
        # Start the updater for db procedures
        from ScheduledTasks import updater
        updater.start()

