# Generated by Django 3.2 on 2021-04-30 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benevole', '0002_alter_assoorigine_nom'),
        ('evenement', '0006_auto_20210425_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planning',
            name='creneau_moyen',
            field=models.PositiveSmallIntegerField(choices=[(60, 'Une Heure'), (90, 'Une Heure Trente'), (120, 'Deux Heures'), (150, 'Deux Heures Trente'), (180, 'Trois Heures'), (210, 'Trois Heures Trente'), (240, 'Quatre Heures')], default=120, help_text="duree classique d'un créneau en minutes"),
        ),
        migrations.AlterField(
            model_name='poste',
            name='benevole',
            field=models.ManyToManyField(blank=True, default='', help_text='responsable de poste, ca n a surement pas de sens', related_name='BenevolesPoste', to='benevole.ProfileBenevole'),
        ),
    ]
