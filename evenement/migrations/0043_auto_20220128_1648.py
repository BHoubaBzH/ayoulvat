# Generated by Django 3.2.4 on 2022-01-28 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0009_alter_abonnement_formule'),
        ('benevole', '0018_alter_profilebenevole_assopartenaire'),
        ('evenement', '0042_alter_evenement_courriel_organisateur'),
    ]

    operations = [
        migrations.CreateModel(
            name='evenement_benevole_assopart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asso_part', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.SET_NULL, to='association.assopartenaire')),
                ('benevole', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='benevole.profilebenevole')),
                ('evenement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evenement.evenement')),
            ],
        ),
        migrations.RemoveField(
            model_name='evenement',
            name='benevole',
        ),
        migrations.AddField(
            model_name='evenement',
            name='benevole',
            field=models.ManyToManyField(blank=True, default='les benevoles peuvent s inscrire a l envenement', related_name='BenevolesEvenement', through='evenement.evenement_benevole_assopart', to='benevole.ProfileBenevole'),
        ),
    ]
