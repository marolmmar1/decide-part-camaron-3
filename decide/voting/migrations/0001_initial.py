# Generated by Django 4.1 on 2023-12-18 00:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("base", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Question",
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
                ("desc", models.TextField()),
                (
                    "optionSiNo",
                    models.BooleanField(
                        default=False,
                        help_text="Marca esta casilla si quieres limitar las opciones a 'Sí' o 'No'. No podrás añadir más opciones si esta casilla está marcada.",
                    ),
                ),
                (
                    "third_option",
                    models.BooleanField(
                        default=False,
                        help_text="Marca esta casilla para añadir una tercera opción con el valor 'Depende'",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Voting",
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
                ("name", models.CharField(max_length=200)),
                ("desc", models.TextField(blank=True, null=True)),
                (
                    "voting_type",
                    models.CharField(
                        choices=[
                            ("S", "Single Choice"),
                            ("M", "Multiple Choice"),
                            ("H", "Hierarchy"),
                        ],
                        default="S",
                        max_length=1,
                    ),
                ),
                (
                    "postproc_type",
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
                ("tally", models.JSONField(blank=True, null=True)),
                ("postproc", models.JSONField(blank=True, null=True)),
                (
                    "seats",
                    models.PositiveIntegerField(blank=True, default=10, null=True),
                ),
                (
                    "auths",
                    models.ManyToManyField(related_name="votings", to="base.auth"),
                ),
                (
                    "pub_key",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="voting",
                        to="base.key",
                    ),
                ),
                (
                    "questions",
                    models.ManyToManyField(
                        related_name="votings", to="voting.question"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="QuestionOption",
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
                ("number", models.PositiveIntegerField(blank=True, null=True)),
                ("option", models.TextField()),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="options",
                        to="voting.question",
                    ),
                ),
            ],
        ),
    ]
