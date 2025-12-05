from django.apps import AppConfig
import allauth.socialaccount.providers.google


class PaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payment'
