# Generated by Django 3.2 on 2021-05-04 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='abonnement',
            old_name='UUID_abonnement',
            new_name='UUID',
        ),
        migrations.RenameField(
            model_name='association',
            old_name='UUID_association',
            new_name='UUID',
        ),
    ]
