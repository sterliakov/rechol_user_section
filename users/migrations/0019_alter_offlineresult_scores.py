# Generated by Django 4.0.5 on 2022-10-19 22:31

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_remove_offlineresult_paper_annotated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offlineresult',
            name='scores',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(blank=True, default='', max_length=2),
                size=5,
                verbose_name='Scores',
            ),
        ),
    ]