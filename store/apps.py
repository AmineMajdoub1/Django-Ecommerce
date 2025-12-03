from django.apps import AppConfig
import os

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # Only run when deployed on Railway
        if not os.environ.get('RAILWAY_ENVIRONMENT'):
            return

        try:
            from django.contrib.sites.models import Site
            from allauth.socialaccount.models import SocialApp

            GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
            GOOGLE_SECRET_KEY = os.environ.get('GOOGLE_SECRET_KEY')

            if GOOGLE_CLIENT_ID and GOOGLE_SECRET_KEY:
                # Ensure Site ID=1 exists
                site, _ = Site.objects.get_or_create(
                    id=1,
                    defaults={'domain': 'lecisele.com', 'name': 'lecisele.com'}
                )

                # Remove old Google apps
                SocialApp.objects.filter(provider='google').delete()

                # Create a new Google SocialApp
                app = SocialApp.objects.create(
                    provider='google',
                    name='Google',
                    client_id=GOOGLE_CLIENT_ID,
                    secret=GOOGLE_SECRET_KEY,
                )

                # Connect it to the site
                app.sites.add(site)
                print("✔ Google SocialApp created", flush=True)

        except Exception as e:
            print("❌ Google setup error:", e, flush=True)
