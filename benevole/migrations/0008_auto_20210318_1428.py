# Generated by Django 3.1.7 on 2021-03-18 13:28

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('evenement', '0006_auto_20210318_1330'),
        ('benevole', '0007_auto_20210318_1356'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profileorganisateur',
            old_name='UUID_Organisateur',
            new_name='UUID_organisateur',
        ),
        migrations.RenameField(
            model_name='profileresponsable',
            old_name='UUID_Responsable',
            new_name='UUID_responsable',
        ),
        migrations.RemoveField(
            model_name='profileorganisateur',
            name='evenement',
        ),
        migrations.RemoveField(
            model_name='profileresponsable',
            name='equipe',
        ),
        migrations.CreateModel(
            name='ProfileBenevole',
            fields=[
                ('UUID_benevole', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('equipe', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='evenement.equipe')),
                ('personne', models.OneToOneField(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='benevole.profilepersonne')),
            ],
        ),
    ]
