# Generated by Django 3.2.3 on 2021-05-22 15:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0006_assopartenaire'),
        ('benevole', '0006_auto_20210522_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personne',
            name='assopartenaire',
            field=models.ForeignKey(blank=True, default='', help_text='associations partenaires des evenements de cette association', null=True, on_delete=django.db.models.deletion.PROTECT, to='association.assopartenaire'),
        ),
    ]
