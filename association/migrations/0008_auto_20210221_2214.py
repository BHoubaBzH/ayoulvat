# Generated by Django 3.1.7 on 2021-02-21 21:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0007_auto_20210221_2212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abonnement',
            name='UUID_association',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='association.association'),
        ),
    ]
