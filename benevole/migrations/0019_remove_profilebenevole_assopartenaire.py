# Generated by Django 3.2.4 on 2022-01-30 17:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benevole', '0018_alter_profilebenevole_assopartenaire'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profilebenevole',
            name='assopartenaire',
        ),
    ]
