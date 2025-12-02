#!/bin/bash
set -e

echo "Applying database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting Gunicorn..."
exec gunicorn ecom.wsgi \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
