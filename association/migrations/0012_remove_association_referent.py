# Generated by Django 4.1.5 on 2023-04-07 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0011_rename_administrateur_association_referent_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='association',
            name='referent',
        ),
    ]
