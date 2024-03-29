# Generated by Django 4.0.5 on 2022-11-16 10:06
from __future__ import annotations

from django.db import migrations, models
from django.utils import timezone as tz


def create_singleton(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    ConfigurationSingleton = apps.get_model("users", "ConfigurationSingleton")
    ConfigurationSingleton.objects.using(db_alias).create(
        offline_appeal_start=tz.datetime(
            2022, 11, 11, 0, 0, 0, tzinfo=tz.get_default_timezone()
        ),
        offline_appeal_end=tz.datetime(
            2022, 11, 17, 23, 59, 59, tzinfo=tz.get_default_timezone()
        ),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0032_alter_appellation_response"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConfigurationSingleton",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "offline_appeal_start",
                    models.DateTimeField(verbose_name="Start of offline stage appeal"),
                ),
                (
                    "offline_appeal_end",
                    models.DateTimeField(verbose_name="End of offline stage appeal"),
                ),
            ],
            options={
                "verbose_name": "Configuration",
                "verbose_name_plural": "Configurations",
            },
        ),
        migrations.RunPython(create_singleton),
    ]
