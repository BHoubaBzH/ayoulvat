# Generated by Django 3.1.7 on 2021-03-16 11:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0003_auto_20210316_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abonnement',
            name='association',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.SET_NULL, to='association.association'),
        ),
    ]
