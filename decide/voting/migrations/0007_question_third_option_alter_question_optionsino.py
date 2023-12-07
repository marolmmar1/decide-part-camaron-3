# Generated by Django 4.1 on 2023-11-14 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0006_alter_question_optionsino'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='third_option',
            field=models.BooleanField(default=False, help_text='Marca esta casilla para añadir una tercera opción'),
        ),
        migrations.AlterField(
            model_name='question',
            name='optionSiNo',
            field=models.BooleanField(default=False, help_text="Marca esta casilla si quieres limitar las opciones a 'Sí' o 'No'. No podrás añadir más opciones si esta casilla está marcada."),
        ),
    ]
