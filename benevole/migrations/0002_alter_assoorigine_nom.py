# Generated by Django 3.2 on 2021-04-20 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benevole', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assoorigine',
            name='nom',
            field=models.CharField(max_length=50, unique='True', verbose_name='association repésentée par le bénévole'),
        ),
    ]