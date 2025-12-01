"""
Django settings for ecom project on Railway.
Deployed to: lecisele.com
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url  # For Railway database

# ========== BASE DIRECTORY ==========
BASE_DIR = Path(__file__).resolve().parent.parent

# ========== LOAD ENVIRONMENT VARIABLES ==========
dotenv_path = BASE_DIR / ".env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path, override=True)
    print(">>> Loaded local .env file")
else:
    print(">>> No .env file found, using Railway environment variables")

# ========== SECURITY SETTINGS ==========
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'  # False in production

# ALLOWED HOSTS - ADD YOUR DOMAIN HERE
ALLOWED_HOSTS = [
    'lecisele.com',
    'www.lecisele.com',
    '.up.railway.app',  # Railway domain
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
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

ADMINS = [
    ('Site Admin', os.environ.get('ADMIN_EMAIL', 'amine.majdoub02@gmail.com')),
]

# ========== APPLICATION DEFINITION ==========
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Your apps
    'store',
    'cart',
    'payment',
    
    # Third-party apps
    'whitenoise.runserver_nostatic',
    'paypal.standard.ipn',
    'django.contrib.sites',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'ecom.wsgi.application'

# ========== DATABASE CONFIGURATION ==========
# FORCE PostgreSQL detection on Railway
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# AGGRESSIVE PostgreSQL detection for Railway
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_STATIC_URL')

if IS_RAILWAY:
    print(">>> RAILWAY ENVIRONMENT DETECTED")
    
    # Check multiple possible database URL variables
    DATABASE_URL = None
    possible_db_vars = ['DATABASE_URL', 'POSTGRES_URL', 'POSTGRESQL_URL']
    
    for var in possible_db_vars:
        if os.environ.get(var):
            DATABASE_URL = os.environ.get(var)
            print(f">>> Found database URL in {var}")
            break
    
    if DATABASE_URL:
        # Fix URL format for dj-database-url
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')
            print(">>> Fixed PostgreSQL URL format")
        
        try:
            DATABASES['default'] = dj_database_url.parse(DATABASE_URL, conn_max_age=600)
            print(f">>> SUCCESS: Using PostgreSQL database: {DATABASES['default']['NAME']}")
            print(f">>> Database engine: {DATABASES['default']['ENGINE']}")
        except Exception as e:
            print(f">>> ERROR connecting to PostgreSQL: {e}")
            print(">>> Falling back to SQLite for now")
    else:
        print(">>> WARNING: No DATABASE_URL found!")
        print(">>> Please add PostgreSQL database in Railway dashboard")
        print(">>> Using SQLite temporarily - ADD POSTGRESQL DATABASE!")
else:
    print(">>> Local development: Using SQLite")

# ========== PASSWORD VALIDATION ==========
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ========== INTERNATIONALIZATION ==========
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ========== STATIC & MEDIA FILES ==========
# Static files configuration for production
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Whitenoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_ROOT = os.path.join(BASE_DIR, 'staticfiles')
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ========== DEFAULT PRIMARY KEY ==========
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== PAYPAL SETTINGS ==========
PAYPAL_TEST = os.environ.get('PAYPAL_TEST', 'True') == 'True'
PAYPAL_RECEIVER_EMAIL = os.environ.get('PAYPAL_RECEIVER_EMAIL', 'business@codemytest.com')
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', '')

# ========== ALLAUTH SETTINGS ==========
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# ========== RAILWAY PRODUCTION SETTINGS ==========
# Force HTTPS and security on Railway
if IS_RAILWAY or not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    print(">>> Production security settings enabled")

# ========== AUTO-CREATE ADMIN USER ==========
# Create admin user automatically on Railway
if IS_RAILWAY and os.environ.get('CREATE_ADMIN', 'True') == 'True':
    try:
        # Import inside function to avoid circular imports
        from django.contrib.auth import get_user_model
        from django.db.utils import OperationalError
        
        User = get_user_model()
        
        # Check if admin exists
        try:
            if not User.objects.filter(username='admin').exists():
                print(">>> Creating admin user...")
                User.objects.create_superuser(
                    username='admin',
                    email='admin@lecisele.com',
                    password='AdminPassword123'
                )
                print(">>> Admin user created successfully!")
            else:
                print(">>> Admin user already exists")
        except OperationalError:
            print(">>> Database not ready yet, skipping admin creation")
    except Exception as e:
        print(f">>> Error in admin creation: {e}")

# ========== FIX PAGINATION WARNING ==========
# Add default ordering to avoid warning
SILENCED_SYSTEM_CHECKS = ['models.W042']
# ========== CREATE ADMIN AFTER SETUP ==========
import sys

# Only run when starting server
if "gunicorn" in sys.argv or "runserver" in sys.argv:
    # Delay import until Django is ready
    import threading
    import time
    
    def delayed_admin_creation():
        time.sleep(5)  # Wait for Django to be ready
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser("admin", "admin@lecisele.com", "AdminPassword123")
                print(">>> Admin user created successfully!")
            else:
                print(">>> Admin user already exists")
        except Exception as e:
            print(f">>> Admin creation skipped: {e}")
    
    # Run in background thread
    thread = threading.Thread(target=delayed_admin_creation, daemon=True)
    thread.start()
