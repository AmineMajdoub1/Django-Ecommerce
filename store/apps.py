from django.apps import AppConfig
import allauth.socialaccount.providers.google

import os

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
