# Generated by Django 3.1.7 on 2021-03-15 22:20

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('association', '0001_initial'),
        ('benevole', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipe',
            fields=[
                ('UUID_equipe', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nom', models.CharField(max_length=50)),
                ('responsable_valide', models.BooleanField(help_text='les responsables doivent valider les créneaux choisis')),
                ('responsable_creer', models.BooleanField(help_text='les responsables peuvent creer des bénévoles')),
                ('description', models.CharField(blank=True, default='', max_length=500)),
                ('UUID_benevole', models.ManyToManyField(related_name='Responsable', to='benevole.ProfileResponsable')),
            ],
        ),
        migrations.CreateModel(
            name='Planning',
            fields=[
                ('UUID_planning', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nom', models.CharField(max_length=50)),
                ('debut', models.DateTimeField()),
                ('fin', models.DateTimeField()),
                ('creneaux', models.BooleanField(help_text='par créneaux fixes ou par entrée libre des bénévoles')),
                ('ouvert_mineur', models.BooleanField(default=True, help_text="possibilité de bloquer l'accès aux mineurs, ex : BAR")),
                ('description', models.CharField(blank=True, default='', max_length=500)),
                ('UUID_equipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evenement.equipe')),
            ],
        ),
        migrations.CreateModel(
            name='Poste',
            fields=[
                ('UUID_poste', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nom', models.CharField(max_length=50)),
                ('planning', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evenement.planning')),
            ],
        ),
        migrations.CreateModel(
            name='Evenement',
            fields=[
                ('UUID_evenement', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nom', models.CharField(max_length=50)),
                ('date_debut', models.DateField()),
                ('date_fin', models.DateField()),
                ('site_web', models.URLField(blank=True, default='')),
                ('editable', models.BooleanField(help_text='inscription ouvertes ou non')),
                ('description', models.CharField(blank=True, default='', max_length=500)),
                ('UUID_association', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='association.association')),
                ('UUID_benevole', models.ManyToManyField(related_name='Organisateur', to='benevole.ProfileOrganisateur')),
            ],
        ),
        migrations.AddField(
            model_name='equipe',
            name='UUID_evenement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evenement.evenement'),
        ),
        migrations.CreateModel(
            name='Creneau',
            fields=[
                ('UUID_creneau', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nom', models.CharField(blank=True, default='', help_text='laisser vide, le champs sera rempli automatiquement', max_length=80)),
                ('debut', models.DateTimeField(default='')),
                ('fin', models.DateTimeField(default='')),
                ('description', models.CharField(blank=True, default='', max_length=500)),
                ('UUID_benevole', models.OneToOneField(default='', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='benevole.profilebenevole')),
                ('poste', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='evenement.poste')),
            ],
            options={
                'verbose_name_plural': 'Creneaux',
            },
        ),
    ]
