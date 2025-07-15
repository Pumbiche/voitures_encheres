#!/usr/bin/env bash

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input