"""
Django settings for ecom project on Railway.
Deployed to: lecisele.com
"""

from pathlib import Path
import os
import dj_database_url

# ========== BASE DIRECTORY ==========
BASE_DIR = Path(__file__).resolve().parent.parent

# ========== SECURITY SETTINGS ==========
# SET TO True TO SEE ERRORS, CHANGE TO False AFTER SITE WORKS
DEBUG = True  # TEMPORARY - Change to False after site works

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production-12345')

# ========== ALLOWED HOSTS ==========
ALLOWED_HOSTS = [
    'lecisele.com',
    'www.lecisele.com',
    '.up.railway.app',
    'localhost',
    '127.0.0.1',
    '*',  # TEMPORARY - REMOVE WHEN SITE WORKS
]

# ========== CSRF PROTECTION ==========
CSRF_TRUSTED_ORIGINS = [
    'https://lecisele.com',
    'https://www.lecisele.com',
    'https://*.up.railway.app',
]

# ========== APPLICATION DEFINITION ==========
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Your apps
    'store',
    'cart',
    'payment',
    
    # Third-party apps
    'whitenoise.runserver_nostatic',
    'paypal.standard.ipn',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'sorl.thumbnail',
    # REMOVED: 'debug_toolbar',  # Remove for production
]

SITE_ID = 1

# ========== MIDDLEWARE ==========
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
    # REMOVED: 'debug_toolbar.middleware.DebugToolbarMiddleware',  # Remove for production
]

# ========== URL & TEMPLATE CONFIGURATION ==========
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

# ========== DATABASE CONFIGURATION ==========
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        ssl_require=True
    )
}

# ========== PASSWORD VALIDATION ==========
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========== INTERNATIONALIZATION ==========
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ========== STATIC FILES ==========
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ========== MEDIA FILES ==========
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ========== DEFAULT PRIMARY KEY ==========
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== ALLAUTH SETTINGS ==========
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# ========== PAYPAL SETTINGS ==========
PAYPAL_TEST = True
PAYPAL_RECEIVER_EMAIL = 'business@codemytest.com'

# ========== LOGGING FOR DEBUGGING ==========
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# ========== PRODUCTION SECURITY ==========
# ONLY ENABLE WHEN DEBUG = False
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ========== AUTO-CREATE ADMIN & FIX SOCIALAPP ==========
import sys

if os.environ.get('RAILWAY_ENVIRONMENT'):
    try:
        import django
        django.setup()
        
        # 1. Create admin user if doesn't exist
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@lecisele.com',
                password='admin123'  # CHANGE THIS PASSWORD!
            )
            print("✅ Admin user created: admin / admin123", file=sys.stderr)
        else:
            print("✅ Admin user already exists", file=sys.stderr)
        
        # 2. Create dummy Google SocialApp to fix 500 error
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site
        
        site = Site.objects.get(id=1)
        
        if not SocialApp.objects.filter(provider='google').exists():
            app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id='dummy-client-id',
                secret='dummy-secret-key',
            )
            app.sites.add(site)
            print("✅ Dummy Google SocialApp created", file=sys.stderr)
        else:
            print("✅ Google SocialApp already exists", file=sys.stderr)
            
    except Exception as e:
        print(f"⚠️ Startup error: {e}", file=sys.stderr)