from django.apps import AppConfig


class AhjConfig(AppConfig):
    name = 'ahj_app'

    # override the ready method to call the updater
    # start method. ScheduledTasks is a module that
    # allows us to update the registry at timed intervals
    def ready(self) -> None:
        # TODO why is this marked as unresolved, it works?
        from ScheduledTasks import updater
        updater.start()

