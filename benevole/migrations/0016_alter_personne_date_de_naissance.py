# Generated by Django 3.2.4 on 2021-08-22 19:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benevole', '0015_alter_personne_date_de_naissance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personne',
            name='date_de_naissance',
            field=models.DateField(default=datetime.datetime(2001, 8, 22, 19, 40, 39, 321578), null=True),
        ),
    ]