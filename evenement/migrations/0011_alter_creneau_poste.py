# Generated by Django 3.2 on 2021-05-01 10:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evenement', '0010_alter_creneau_poste'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creneau',
            name='poste',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='evenement.poste'),
        ),
    ]
