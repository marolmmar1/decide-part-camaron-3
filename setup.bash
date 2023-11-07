cd "${0%/*}"
cd decide
cp local_settings.example.py local_settings.py
sed -i "s/10.*:/localhost:/" local_settings.py
sed -i "s/'NAME': 'postgres'/'NAME': 'decidedb'/" local_settings.py
sed -i "s/'USER': 'postgres'/'USER': 'decideuser'/" local_settings.py
sed -i "s/'HOST': 'db'/'HOST': 'localhost',\n        'PASSWORD': 'decidepass123'/" local_settings.py
echo "Created local_settings.py"
cd ..
python -m venv venv
source venv/bin/activate
echo "Created Python virtual environment"
pip install -r requirements.txt
sudo su - postgres <<EOF
psql -c "drop database if exists decidedb"
psql -c "drop user if exists decideuser"
psql -c "create user decideuser with password 'decidepass123'"
psql -c "create database decidedb owner decideuser"
psql -c "ALTER USER decideuser CREATEDB"
EOF
echo "Created database"
cd decide
python manage.py migrate
python manage.py createsuperuser --noinput --username admin --email admin@us.es
python manage.py shell <<EOF
from django.contrib.auth.models import User
u = User.objects.all()[0]
u.set_password('admin')
u.save()
EOF
