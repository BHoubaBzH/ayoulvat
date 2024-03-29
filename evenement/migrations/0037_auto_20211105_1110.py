# Generated by Django 3.2.4 on 2021-11-05 11:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evenement', '0036_auto_20210825_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipe',
            name='seuil1',
            field=models.IntegerField(default=50, help_text='pourcentage à partir du quel la stat du dashboard devient jaune', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='equipe',
            name='seuil2',
            field=models.IntegerField(default=80, help_text='pourcentage à partir du quel la stat du dashboard devient vert', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='planning',
            name='seuil1',
            field=models.IntegerField(default=50, help_text='pourcentage à partir du quel la stat du dashboard devient jaune', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='planning',
            name='seuil2',
            field=models.IntegerField(default=80, help_text='pourcentage à partir du quel la stat du dashboard devient vert', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
