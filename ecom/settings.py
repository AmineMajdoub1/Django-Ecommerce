"""
Django settings for ecom project on Railway.
Deployed to: lecisele.com
"""

from pathlib import Path
import os
import sys
import threading
import time
from dotenv import load_dotenv
import dj_database_url

# ========== BASE DIRECTORY ==========
BASE_DIR = Path(__file__).resolve().parent.parent

# ========== LOAD ENVIRONMENT VARIABLES ==========
# Try to load .env file if exists, but don't require dotenv package
try:
    from dotenv import load_dotenv
    dotenv_path = BASE_DIR / ".env"
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path, override=True)
        print(">>> Loaded local .env file")
    else:
        print(">>> No .env file found")
except ImportError:
    # dotenv not installed, use environment variables directly
    print(">>> Using environment variables directly")
    pass

# Import dj-database-url with fallback
try:
    import dj_database_url
    DJ_DATABASE_URL_AVAILABLE = True
except ImportError:
    DJ_DATABASE_URL_AVAILABLE = False
    print(">>> Warning: dj-database-url not available")

# ========== SECURITY SETTINGS ==========
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production-12345')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED HOSTS
ALLOWED_HOSTS = [
    'lecisele.com',
    'www.lecisele.com',
    '.up.railway.app',
    'localhost',
    '127.0.0.1',
]

# CSRF PROTECTION
CSRF_TRUSTED_ORIGINS = [
    'https://lecisele.com',
    'https://www.lecisele.com',
    'https://*.up.railway.app',
]

# ========== EMAIL SETTINGS ==========
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

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
]

SITE_ID = 1

# ========== MIDDLEWARE ==========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # MUST BE HERE for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'store.social_cart_middleware.SocialLoginCartMiddleware',
]

# ========== URL & TEMPLATE CONFIGURATION ==========
ROOT_URLCONF = 'ecom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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
# PostgreSQL on Railway, SQLite locally
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Force PostgreSQL on Railway
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('DATABASE_URL'):
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    if DATABASE_URL:
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')
        try:
            DATABASES['default'] = dj_database_url.parse(DATABASE_URL, conn_max_age=600)
            print(">>> SUCCESS: Connected to PostgreSQL on Railway")
        except Exception as e:
            print(f">>> PostgreSQL error: {e}")
            print(">>> Using SQLite as fallback")
    else:
        print(">>> WARNING: No DATABASE_URL found on Railway")
else:
    print(">>> Local development: Using SQLite")

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

# ========== STATIC FILES - FIXED FOR PRODUCTION ==========
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Whitenoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_ROOT = STATIC_ROOT
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False

# ========== MEDIA FILES ==========
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ========== DEFAULT PRIMARY KEY ==========
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== PAYPAL SETTINGS ==========
PAYPAL_TEST = os.environ.get('PAYPAL_TEST', 'True') == 'True'
PAYPAL_RECEIVER_EMAIL = os.environ.get('PAYPAL_RECEIVER_EMAIL', 'business@codemytest.com')

# ========== ALLAUTH SETTINGS ==========
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# ========== PRODUCTION SECURITY ==========
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    print(">>> Production security enabled")

# ========== AUTO-CREATE ADMIN USER ==========
def create_admin_user():
    """Create admin user after Django is fully loaded"""
    time.sleep(5)  # Wait for Django to initialize
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@lecisele.com',
                password='AdminPassword123'
            )
            print(">>> ✅ Admin user created successfully!")
        else:
            print(">>> ℹ️ Admin user already exists")
    except Exception as e:
        print(f">>> ⚠️ Admin creation skipped: {str(e)[:100]}")

# Start admin creation in background thread
if 'gunicorn' in sys.argv or 'runserver' in sys.argv:
    admin_thread = threading.Thread(target=create_admin_user, daemon=True)
    admin_thread.start()