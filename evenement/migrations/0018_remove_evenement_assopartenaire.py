# Generated by Django 3.2.3 on 2021-05-22 15:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evenement', '0017_evenement_assopartenaire'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evenement',
            name='assopartenaire',
        ),
    ]
