#!/usr/bin/env bash
set -e

echo "Install dependencies"
pip install -r requirements.txt

echo "Run migrations"
python manage.py migrate --noinput

echo "Collect static files"
python manage.py collectstatic --noinput
