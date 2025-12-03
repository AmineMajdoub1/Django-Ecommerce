"""
Django settings for ecom project on Railway.
"""

from pathlib import Path
import os
import dj_database_url
import sys

# ========= BASE DIR ==========
BASE_DIR = Path(__file__).resolve().parent.parent

# ========= SECURITY ==========
DEBUG = True  # Set to FALSE after everything works

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-temp-key-change-in-production')

# ========= ALLOWED HOSTS ==========
ALLOWED_HOSTS = [
    'lecisele.com',
    'www.lecisele.com',
    '.up.railway.app',
    'localhost',
    '*'
]

# ========= CSRF ==========
CSRF_TRUSTED_ORIGINS = [
    'https://lecisele.com',
    'https://www.lecisele.com',
    'https://*.up.railway.app',
]

# ========= INSTALLED APPS ==========
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # apps
    'store',
    'cart',
    'payment',

    # third-party
    'whitenoise.runserver_nostatic',
    'paypal.standard.ipn',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'sorl.thumbnail',
]

SITE_ID = 1

# ========= MIDDLEWARE ==========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'store.social_cart_middleware.SocialLoginCartMiddleware',
]

# ========= TEMPLATES ==========
ROOT_URLCONF = 'ecom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart',
                'store.context_processors.wishlist_count',
                'store.context_processors.categories',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecom.wsgi.application'

# ========= DATABASE ==========
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        ssl_require=True
    )
}

# ========= PASSWORDS ==========
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========= I18N ==========
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ========= STATIC ==========
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ========= MEDIA ==========
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========= ALLAUTH ==========
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# ========= PAYPAL ==========
PAYPAL_TEST = True
PAYPAL_RECEIVER_EMAIL = 'business@codemytest.com'

# ========= LOGGING ==========
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# ========= PRODUCTION SECURITY ==========
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# ========= RAILWAY AUTO FIX (ADMIN + SITE + GOOGLE) ==========
if os.environ.get('RAILWAY_ENVIRONMENT'):
    try:
        import django
        django.setup()

        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@lecisele.com',
                password='admin123'
            )
            print("Admin auto-created", file=sys.stderr)

        # Fix site
        from django.contrib.sites.models import Site
        site, _ = Site.objects.get_or_create(
            id=1,
            defaults={'domain': 'lecisele.com', 'name': 'lecisele.com'}
        )
        site.domain = 'lecisele.com'
        site.name = 'lecisele.com'
        site.save()

        # Create Google SocialApp from Railway variables
        from allauth.socialaccount.models import SocialApp

        GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
        GOOGLE_SECRET_KEY = os.environ.get('GOOGLE_SECRET_KEY')

        if GOOGLE_CLIENT_ID and GOOGLE_SECRET_KEY:
            SocialApp.objects.filter(provider='google').delete()
            app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id=GOOGLE_CLIENT_ID,
                secret=Google_SECRET_KEY,
            )
            app.sites.add(site)
            print("Google OAuth App created", file=sys.stderr)

    except Exception as e:
        print(f"Error in Railway setup: {e}", file=sys.stderr)
