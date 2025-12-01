import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecom.settings")
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@lecisele.com", "AdminPassword123")
    print(">>> Admin user created!")
else:
    print(">>> Admin user exists")
