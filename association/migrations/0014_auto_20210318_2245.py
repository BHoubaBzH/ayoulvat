# Generated by Django 3.1.7 on 2021-03-18 21:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0013_auto_20210318_2245'),
    ]

    operations = [
        migrations.RenameField(
            model_name='association',
            old_name='administrateurb',
            new_name='administrateur',
        ),
    ]
