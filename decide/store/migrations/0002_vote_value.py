# Generated by Django 4.1 on 2023-12-18 13:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="vote",
            name="value",
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
