# Generated by Django 4.2.15 on 2024-09-18 01:34
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0059_alter_organizercertificate_first_name_gen_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="venue",
            name="full_name",
            field=models.CharField(max_length=255, verbose_name="full name"),
        ),
    ]
