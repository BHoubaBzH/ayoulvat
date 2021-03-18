# Generated by Django 3.1.7 on 2021-03-18 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benevole', '0009_auto_20210318_1442'),
        ('evenement', '0010_equipe_benevole'),
    ]

    operations = [
        migrations.AddField(
            model_name='planning',
            name='benevole',
            field=models.ManyToManyField(default='', related_name='BenevolesPlanning', to='benevole.ProfileBenevole'),
        ),
        migrations.AddField(
            model_name='poste',
            name='benevole',
            field=models.ManyToManyField(default='', related_name='BenevolesPoste', to='benevole.ProfileBenevole'),
        ),
        migrations.RemoveField(
            model_name='creneau',
            name='benevole',
        ),
        migrations.AddField(
            model_name='creneau',
            name='benevole',
            field=models.ManyToManyField(default='', related_name='BenevolesCreneau', to='benevole.ProfileBenevole'),
        ),
        migrations.AlterField(
            model_name='equipe',
            name='benevole',
            field=models.ManyToManyField(default='', related_name='BenevolesEquipe', to='benevole.ProfileBenevole'),
        ),
        migrations.AlterField(
            model_name='equipe',
            name='responsable',
            field=models.ManyToManyField(default='', related_name='ResponsableEquipe', to='benevole.ProfileResponsable'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='benevole',
            field=models.ManyToManyField(default='', related_name='BenevolesEvenement', to='benevole.ProfileBenevole'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='organisateur',
            field=models.ManyToManyField(default='', related_name='OrganisateurEvenement', to='benevole.ProfileOrganisateur'),
        ),
    ]
