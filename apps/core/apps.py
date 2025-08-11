from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self):
        try:
            from .auth import ensure_roles_exist
            ensure_roles_exist()
        except Exception:
            # DB might not be ready during migrations/collectstatic
            pass