# Generated by Django 4.1 on 2023-12-18 00:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("voting", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PostProcessing",
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
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("NON", "NONE"),
                            ("DHO", "DHONDT"),
                            ("PAR", "SAINT"),
                            ("DRO", "DROOP"),
                        ],
                        default="NON",
                        max_length=3,
                    ),
                ),
                ("start_date", models.DateTimeField(blank=True, null=True)),
                ("end_date", models.DateTimeField(blank=True, null=True)),
                ("results", models.JSONField(blank=True, null=True)),
                (
                    "question",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="voting.question",
                    ),
                ),
                (
                    "voting",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="voting.voting",
                    ),
                ),
            ],
            options={
                "unique_together": {("voting_id", "question_id", "type")},
            },
        ),
    ]
