#!/usr/bin/env sh

# Generate static files for nginx to serve
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate --noinput

# Run wsgi server
gunicorn --bind 0.0.0.0:8000 cookTogether.wsgi:application