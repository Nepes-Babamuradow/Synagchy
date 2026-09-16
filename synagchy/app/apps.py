from django.apps import AppConfig
from django.db.models.signals import post_migrate


def _run_initial_data(sender, **kwargs):
    try:
        from .initial_data import create_initial_data
        create_initial_data()
    except Exception:
        # Avoid breaking migrations if seeding fails; log to stdout
        import sys
        print('initial_data: failed to run seeding', file=sys.stderr)


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        post_migrate.connect(_run_initial_data, sender=self)
