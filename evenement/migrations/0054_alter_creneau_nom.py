# Generated by Django 4.0.2 on 2022-03-29 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evenement', '0052_evenement_commentaire_alter_creneau_nom_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creneau',
            name='nom',
            field=models.CharField(blank=True, default='', help_text='le champs sera écrasé automatiquement', max_length=200),
        ),
    ]
