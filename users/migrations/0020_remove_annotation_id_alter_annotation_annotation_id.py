# Generated by Django 4.0.5 on 2022-10-19 22:52
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0019_alter_offlineresult_scores"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="annotation",
            name="id",
        ),
        migrations.AlterField(
            model_name="annotation",
            name="annotation_id",
            field=models.UUIDField(
                primary_key=True, serialize=False, verbose_name="Annotation ID"
            ),
        ),
    ]
