from django.apps import AppConfig


class UtilsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "utils"

    def ready(self):
        # Import tasks when the app is ready to ensure they're registered with Celery
        try:
            from . import tasks
        except ImportError:
            pass
