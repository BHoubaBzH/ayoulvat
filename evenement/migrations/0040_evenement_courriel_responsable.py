# Generated by Django 3.2.4 on 2022-01-24 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evenement', '0039_auto_20220124_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='evenement',
            name='courriel_responsable',
            field=models.EmailField(default='', help_text='courriel accessible aux bénévoles en bas de page', max_length=254),
        ),
    ]
