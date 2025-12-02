#!/bin/bash
set -e

echo "🚀 Starting Django application on Railway..."

echo "1. Applying database migrations..."
python manage.py migrate --noinput

echo "2. Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "3. Creating admin user if doesn't exist..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@lecisele.com', 'admin123')
    print('✅ Admin user created')
else:
    print('✅ Admin user already exists')
"

echo "4. Fixing site configuration..."
python manage.py shell -c "
from django.contrib.sites.models import Site
try:
    site = Site.objects.get(id=1)
    if site.domain != 'lecisele.com':
        site.domain = 'lecisele.com'
        site.name = 'lecisele.com'
        site.save()
        print(f'✅ Site updated to: {site.domain}')
    else:
        print(f'✅ Site already correct: {site.domain}')
except Exception as e:
    print(f'❌ Error fixing site: {e}')
"

echo "5. Creating Google SocialApp for OAuth..."
python manage.py shell -c "
import os
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

print('=== Google OAuth Setup ===')

# Get credentials from environment
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_SECRET_KEY = os.environ.get('GOOGLE_SECRET_KEY')

print(f'Client ID found: {\"✅\" if GOOGLE_CLIENT_ID else \"❌\"}')
print(f'Secret Key found: {\"✅\" if GOOGLE_SECRET_KEY else \"❌\"}')

if not GOOGLE_CLIENT_ID or not GOOGLE_SECRET_KEY:
    print('❌ ERROR: Google OAuth credentials missing!')
    print('   Please add GOOGLE_CLIENT_ID and GOOGLE_SECRET_KEY in Railway Variables')
    print('   Current Client ID:', os.environ.get('GOOGLE_CLIENT_ID', 'Not set'))
    print('   Current Secret:', 'Set' if os.environ.get('GOOGLE_SECRET_KEY') else 'Not set')
else:
    # Get or fix site
    site = Site.objects.get(id=1)
    
    # Delete any existing Google apps
    deleted_count, _ = SocialApp.objects.filter(provider='google').delete()
    if deleted_count > 0:
        print(f'✅ Deleted {deleted_count} old Google SocialApp(s)')
    
    # Create new Google SocialApp
    try:
        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=GOOGLE_CLIENT_ID.strip(),
            secret=GOOGLE_SECRET_KEY.strip(),
        )
        app.sites.add(site)
        app.save()
        
        print('✅ SUCCESS: Google SocialApp created in database!')
        print(f'   Provider: {app.provider}')
        print(f'   Client ID starts with: {app.client_id[:20]}...')
        print(f'   Associated with site: {site.domain}')
        
        # Verify creation
        count = SocialApp.objects.filter(provider='google').count()
        print(f'   Total Google apps in DB: {count}')
        
    except Exception as e:
        print(f'❌ Failed to create SocialApp: {e}')
        import traceback
        traceback.print_exc()

print('=== Google Setup Complete ===')
"

echo "6. Final verification..."
python manage.py shell -c "
from allauth.socialaccount.models import SocialApp
count = SocialApp.objects.filter(provider='google').count()
print(f'🔍 Verification: Found {count} Google SocialApp(s) in database')
if count == 0:
    print('❌ WARNING: No Google SocialApp found! Login with Google will fail.')
else:
    print('✅ Google OAuth should work now!')
"

echo "7. Starting Gunicorn server..."
exec gunicorn ecom.wsgi \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --timeout 120