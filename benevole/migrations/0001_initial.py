# Generated by Django 3.2 on 2021-04-15 22:54

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('association', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Personne',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('UUID_personne', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('role', models.CharField(blank=True, default='', max_length=50)),
                ('genre', models.CharField(choices=[('MINEUR', 'Mineur'), ('HOMME', 'Homme'), ('FEMME', 'Femme'), ('NSP', 'Ne se prononce pas')], default='NSP', max_length=50)),
                ('date_de_naissance', models.DateField(default='2000-01-01')),
                ('fixe', phonenumber_field.modelfields.PhoneNumberField(blank=True, help_text='donn??e optionnelle', max_length=128, null=True, region=None)),
                ('portable', phonenumber_field.modelfields.PhoneNumberField(help_text='donn??e obligatoire', max_length=128, region=None)),
                ('description', models.CharField(blank=True, default='', max_length=500)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AssoOrigine',
            fields=[
                ('UUID_assoorigine', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nom', models.CharField(max_length=50, verbose_name='association rep??sent??e par le b??n??vole')),
            ],
        ),
        migrations.CreateModel(
            name='ProfileResponsable',
            fields=[
                ('UUID_responsable', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('personne', models.OneToOneField(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileOrganisateur',
            fields=[
                ('UUID_organisateur', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('personne', models.OneToOneField(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileBenevole',
            fields=[
                ('UUID_benevole', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('message', models.TextField(blank=True, default='', max_length=1000)),
                ('personne', models.OneToOneField(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileAdministrateur',
            fields=[
                ('UUID_administrateur', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('referent', models.BooleanField(default=False)),
                ('association', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='association.association')),
                ('personne', models.OneToOneField(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='personne',
            name='assoorigine',
            field=models.ForeignKey(blank=True, default='', help_text='association pour la quelle le benevole travaille', null=True, on_delete=django.db.models.deletion.PROTECT, to='benevole.assoorigine'),
        ),
        migrations.AddField(
            model_name='personne',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='personne',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
