# Generated by Django 3.1.7 on 2021-02-21 17:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0004_formule_description'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Formule',
        ),
        migrations.DeleteModel(
            name='Logs',
        ),
    ]
