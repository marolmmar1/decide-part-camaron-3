# Generated by Django 4.1 on 2023-12-17 01:52

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="vote",
            name="value",
        ),
    ]
