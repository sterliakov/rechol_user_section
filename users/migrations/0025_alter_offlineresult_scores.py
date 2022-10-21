# Generated by Django 4.0.5 on 2022-10-21 19:08

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_offlineresult_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offlineresult',
            name='scores',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(blank=True, default='', max_length=2),
                blank=True,
                default=list,
                size=6,
                verbose_name='Scores',
            ),
        ),
    ]
