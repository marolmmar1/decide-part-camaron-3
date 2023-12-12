#!/bin/bash
cd decide/
cp local_settings.deploy.py local_settings.py
./manage.py collectstatic --noinput
./manage.py makemigrations
./manage.py migrate 
./manage.py createsuperuser --noinput --username admin --email admin@camaron.com
gunicorn -w 5 decide.wsgi:application --timeout=500