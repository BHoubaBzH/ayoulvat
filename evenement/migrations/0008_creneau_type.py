# Generated by Django 3.2 on 2021-05-01 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evenement', '0007_auto_20210430_0836'),
    ]

    operations = [
        migrations.AddField(
            model_name='creneau',
            name='type',
            field=models.CharField(choices=[('creneau', 'Creneau'), ('benevole', 'Disponibilité')], default='creneau', help_text='creneau ou dispos de bénévole', max_length=50),
        ),
    ]
