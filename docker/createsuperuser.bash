python manage.py createsuperuser --noinput --username admin --email admin@us.es
python manage.py shell <<EOF
from django.contrib.auth.models import User
u = User.objects.all()[0]
u.set_password('admin')
u.save()
EOF