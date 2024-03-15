# Generated by Django 4.0.5 on 2022-10-17 12:47
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0013_alter_user_passport"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="online_selected",
            field=models.BooleanField(default=True, verbose_name="Online stage"),
        ),
    ]
