# Generated by Django 3.2.4 on 2021-06-28 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evenement', '0022_creneau_valide_present'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creneau',
            name='valide_present',
            field=models.BooleanField(default=True, help_text="à valider si le bénévole s'est bien présenté"),
        ),
    ]
