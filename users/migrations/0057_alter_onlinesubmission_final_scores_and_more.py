# Generated by Django 4.0.10 on 2024-01-19 15:49

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0056_onlineproblem_closes_en"),
    ]

    operations = [
        migrations.AlterField(
            model_name="onlinesubmission",
            name="final_scores",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(blank=True, default="", max_length=4),
                blank=True,
                default=list,
                size=4,
                verbose_name="Final scores after appeal",
            ),
        ),
        migrations.CreateModel(
            name="OrganizerCertificate",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name="id",
                    ),
                ),
                (
                    "first_name_gen",
                    models.CharField(
                        max_length=255, verbose_name="first name (genitiv)"
                    ),
                ),
                (
                    "last_name_gen",
                    models.CharField(
                        max_length=255, verbose_name="last name (genitiv)"
                    ),
                ),
                (
                    "middle_name_gen",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="middle name (genitiv)"
                    ),
                ),
                (
                    "venue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="certificates",
                        to="users.venue",
                        verbose_name="venue",
                    ),
                ),
            ],
        ),
    ]
