# Generated by Django 3.2.4 on 2021-08-25 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benevole', '0013_auto_20210801_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personne',
            name='date_de_naissance',
            field=models.DateField(default='2000-01-01', null=True),
        ),
    ]
