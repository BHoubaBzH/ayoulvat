# Generated by Django 3.2.4 on 2021-08-22 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evenement', '0033_alter_poste_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creneau',
            name='description',
            field=models.TextField(blank=True, default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='equipe',
            name='description',
            field=models.TextField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='description',
            field=models.TextField(blank=True, default='', max_length=2000),
        ),
    ]
