# Generated by Django 4.0.5 on 2022-10-20 17:37
from __future__ import annotations

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0021_alter_user_actual_form_alter_user_birth_date_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="offlineresult",
            name="scores",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(blank=True, default="", max_length=2),
                blank=True,
                size=5,
                verbose_name="Scores",
            ),
        ),
    ]
