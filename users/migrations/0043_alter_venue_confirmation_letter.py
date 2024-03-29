# Generated by Django 4.0.5 on 2023-09-16 13:06
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0042_venue_confirmation_letter_venue_contact_phone_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="venue",
            name="confirmation_letter",
            field=models.FileField(
                help_text="A photo or scan of a confirmation signed by your institution authority",
                null=True,
                upload_to="venue_confirmation_letters",
                verbose_name="Confirmation letter",
            ),
        ),
    ]
