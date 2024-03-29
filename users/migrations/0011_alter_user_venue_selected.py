# Generated by Django 4.0.5 on 2022-10-04 00:13
from __future__ import annotations

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0010_alter_event_options_alter_user_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="venue_selected",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="users.venue",
                verbose_name="Venue",
            ),
        ),
    ]
