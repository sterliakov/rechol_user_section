# Generated by Django 4.0.10 on 2024-01-19 16:02

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0057_alter_onlinesubmission_final_scores_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="organizercertificate",
            options={
                "verbose_name": "organizer certificate",
                "verbose_name_plural": "organizer certificates",
            },
        ),
    ]
