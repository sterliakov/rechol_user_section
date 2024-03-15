# Generated by Django 4.0.5 on 2022-10-20 17:39
from __future__ import annotations

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0022_alter_offlineresult_scores"),
    ]

    operations = [
        migrations.AlterField(
            model_name="offlineresult",
            name="scores",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(blank=True, default="", max_length=2),
                blank=True,
                default=list,
                size=5,
                verbose_name="Scores",
            ),
        ),
    ]
