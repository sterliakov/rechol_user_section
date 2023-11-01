# Generated by Django 4.0.5 on 2022-11-16 10:38

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0033_configurationsingleton"),
    ]

    operations = [
        migrations.AlterField(
            model_name="offlineresult",
            name="final_scores",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(blank=True, default="", max_length=4),
                blank=True,
                default=list,
                size=6,
                verbose_name="Final scores after appellation",
            ),
        ),
        migrations.AlterField(
            model_name="offlineresult",
            name="scores",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(blank=True, default="", max_length=4),
                blank=True,
                default=list,
                size=6,
                verbose_name="Scores",
            ),
        ),
    ]
