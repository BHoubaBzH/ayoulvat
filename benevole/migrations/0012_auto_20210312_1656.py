# Generated by Django 3.1.7 on 2021-03-12 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('benevole', '0011_auto_20210312_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creneau',
            name='UUID_personne',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='benevole.profilepersonne'),
        ),
    ]
