from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.marketplace.categories'
    label = 'categories'
    verbose_name = 'Marketplace Categories'
