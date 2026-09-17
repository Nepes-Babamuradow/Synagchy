from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    label = 'app'

    def ready(self):
        """Post-migrate signal to load initial data."""
        from django.db.models.signals import post_migrate
        from django.dispatch import receiver
        from django.core.management import call_command

        @receiver(post_migrate)
        def load_initial_data(sender, **kwargs):
            if kwargs.get('app_config'):
                app_config = kwargs['app_config']
                if app_config.name == 'app':
                    try:
                        from app.infrastructure.database.models import Subject
                        if not Subject.objects.exists():
                            call_command('loaddata', 'initial_data.json', verbosity=0)
                    except Exception:
                        pass