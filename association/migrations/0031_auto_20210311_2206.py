# Generated by Django 3.1.7 on 2021-03-11 21:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0030_remove_profilegestionnaire_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilegestionnaire',
            name='date_de_naissance',
            field=models.DateField(),
        ),
    ]
