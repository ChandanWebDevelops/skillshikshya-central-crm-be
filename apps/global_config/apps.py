from django.apps import AppConfig


class GlobalConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.global_config'
    verbose_name = 'Global Configuration'
