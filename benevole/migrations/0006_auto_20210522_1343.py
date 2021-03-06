# Generated by Django 3.2.3 on 2021-05-22 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0006_assopartenaire'),
        ('benevole', '0005_rename_uuid_assoorigine_assoorigine_uuid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personne',
            name='assoorigine',
        ),
        migrations.AddField(
            model_name='personne',
            name='assopartenaire',
            field=models.ForeignKey(blank=True, default='', help_text='association pour la quelle le benevole travaille', null=True, on_delete=django.db.models.deletion.PROTECT, to='association.assopartenaire'),
        ),
        migrations.DeleteModel(
            name='AssoOrigine',
        ),
    ]
