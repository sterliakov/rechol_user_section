# Generated by Django 4.0.5 on 2022-10-04 04:03
from __future__ import annotations

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0012_alter_user_passport"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="passport",
            field=models.CharField(
                help_text="Passport in format xxxx xxxxxx or birth proof in format XX-XX xxxxxx",
                max_length=15,
                unique=True,
                validators=[django.core.validators.MinLengthValidator(9)],
                verbose_name="Passport",
            ),
        ),
    ]
