# Generated by Django 3.1.7 on 2021-02-21 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0005_auto_20210221_1819'),
    ]

    operations = [
        migrations.AddField(
            model_name='abonnement',
            name='facture_courriel',
            field=models.EmailField(default='', max_length=254),
        ),
        migrations.AddField(
            model_name='association',
            name='courriel',
            field=models.EmailField(default='', max_length=254),
        ),
    ]
