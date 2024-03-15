# Generated by Django 4.0.5 on 2022-10-25 22:44
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0029_alter_onlinesubmission_file_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="onlineproblem",
            name="target_form",
            field=models.PositiveSmallIntegerField(
                choices=[(8, "8"), (9, "9"), (10, "10"), (11, "11")],
                default=8,
                verbose_name="Target form",
            ),
        ),
    ]
