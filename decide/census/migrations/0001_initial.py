# Generated by Django 4.1 on 2023-12-16 20:45

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Census",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("voting_id", models.PositiveIntegerField()),
                ("voter_id", models.PositiveIntegerField()),
            ],
            options={
                "unique_together": {("voting_id", "voter_id")},
            },
        ),
    ]
