# Generated by Django 3.2 on 2021-04-15 22:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('administration', '0001_initial'),
        ('benevole', '0001_initial'),
        ('association', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='association',
            name='administrateur',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin', to='benevole.profileadministrateur'),
        ),
        migrations.AddField(
            model_name='abonnement',
            name='association',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='association.association'),
        ),
        migrations.AddField(
            model_name='abonnement',
            name='formule',
            field=models.OneToOneField(default='', null=True, on_delete=django.db.models.deletion.PROTECT, to='administration.formule'),
        ),
    ]