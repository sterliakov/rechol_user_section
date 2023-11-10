# Generated by Django 4.0.10 on 2023-11-10 14:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0053_offlineproblem_file_en_offlineproblem_solution_en"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="passport",
            field=models.CharField(
                help_text="Passport in format xxxx xxxxxx or birth proof in format XX-XX xxxxxx",
                max_length=15,
                null=True,
                unique=True,
                validators=[django.core.validators.MinLengthValidator(6)],
                verbose_name="Passport",
            ),
        ),
    ]