from django.apps import AppConfig


class KnStylingConfig(AppConfig):
    name = 'kn_defaults.styling'
    verbose_name = 'KuwaitNet code styling helpers'

    def ready(self):
        super().ready()
        from . import checks
