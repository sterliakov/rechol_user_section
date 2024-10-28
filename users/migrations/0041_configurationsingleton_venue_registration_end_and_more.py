# Generated by Django 4.0.5 on 2023-09-16 12:18
from __future__ import annotations

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0040_configurationsingleton_registration_end_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="configurationsingleton",
            name="venue_registration_end",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 8, 31, 21, 0, tzinfo=datetime.UTC),
                verbose_name="end of venue registration",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="configurationsingleton",
            name="venue_registration_start",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 10, 31, 21, 0, tzinfo=datetime.UTC),
                verbose_name="start of venue registration",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("p", "Participant"),
                    ("a", "Admin"),
                    ("j", "Judge"),
                    ("v", "Venue"),
                ],
                default="p",
                editable=False,
                max_length=1,
                verbose_name="Role",
            ),
        ),
    ]
