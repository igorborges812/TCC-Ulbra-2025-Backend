#!/usr/bin/env sh

# Apply database migrations
python manage.py migrate --noinput

# Run wsgi server
gunicorn --bind 0.0.0.0:8000 cookTogether.wsgi:application