#!/usr/bin/env sh

# apply database migrations
python manage.py migrate --noinput

python manage.py runserver 0.0.0.0:8000