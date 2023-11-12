from django.core.management.base import BaseCommand
from django.conf import settings
from subprocess import call
from cryptography import fernet
import os

class Command(BaseCommand):
    help = 'Save votes in secure backup copy.'

    def handle(self, *args, **options):
        key_path = os.path.join(settings.BASE_DIR, 'backup_key.key')

        if not os.path.exists(key_path):
            key = Fernet.generate_key()
            with open('key_path', 'wb') as key_file:
                key_file.write(key)
        else:
            open('key_path', 'rb') as key_file:
                key = key_file.read()
        cipher_suite = Fernet(key)

        backup_file_path = os.path.join(setting.BASE_DIR, 'backup_file_' + str({timezone.now().strftime("%Y%m%d%H%M%S")}) + '.sql')

        pg_dump_command = [
            'pg-dump',
            '-h', settings.DATABASES['default']['HOST'],
            '-U', settings.DATABASES['default']['USER'],
            '-d', settings.DATABASES['default']['NAME'],
            '-t', '',
            '-f', backup_file_path
        ]

        call(pg_dump_command)
        
        with open(backup_file_path, 'rb') as backup_file:
            encrypted_data = cipher_suite.encrypt(backup_file.read())
        
        encrypted_backup_path = f'{backup_file_path}.enc'
        with open(encrypted_backup_path, 'wb') as encrypted_backup_file:
            encrypted_backup_file.write(encrypted_data)
        os.remove(backup_file_path)

        self.stdout.write(self.style.SUCCESS(f'Backup file created successfully: {encrypted_backup_path}'))
