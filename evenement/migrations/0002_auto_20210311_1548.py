# Generated by Django 3.1.7 on 2021-03-11 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evenement', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipe',
            name='UUID_evenement',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='evenement.evenement'),
        ),
    ]
