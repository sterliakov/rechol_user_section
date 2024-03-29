# Generated by Django 4.0.5 on 2023-09-16 15:26
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0043_alter_venue_confirmation_letter"),
    ]

    operations = [
        migrations.AddField(
            model_name="configurationsingleton",
            name="forbid_venue_change",
            field=models.BooleanField(
                default=False, verbose_name="forbid venue change"
            ),
        ),
    ]
