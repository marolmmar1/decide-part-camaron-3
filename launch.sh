#!/bin/bash
cd decide/
cp local_settings.deploy.py local_settings.py
./manage.py collectstatic --noinput
./manage.py makemigrations
./manage.py migrate 
python manage.py createsuperuser --noinput --username admin --email admin@us.es
python manage.py shell <<EOF
from django.contrib.auth.models import User
u = User.objects.all()[0]
u.set_password('admin')
u.save()
EOF
gunicorn -w 5 decide.wsgi:application --timeout=500