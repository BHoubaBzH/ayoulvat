# Generated by Django 3.2 on 2021-04-20 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('benevole', '0002_alter_assoorigine_nom'),
        ('evenement', '0003_alter_creneau_benevole'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creneau',
            name='benevole',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='BenevolesCreneau', to='benevole.profilebenevole'),
        ),
    ]
