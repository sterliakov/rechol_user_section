# Generated by Django 4.0.10 on 2023-10-23 16:55
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0048_alter_offlineproblem_solution"),
    ]

    operations = [
        migrations.AddField(
            model_name="venue",
            name="is_full",
            field=models.BooleanField(
                default=False, verbose_name="registration closed (full)"
            ),
        ),
    ]
