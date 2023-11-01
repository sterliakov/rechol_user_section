# Generated by Django 4.0.5 on 2022-10-25 22:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0028_alter_onlinesubmission_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="onlinesubmission",
            name="file",
            field=models.FileField(
                help_text="Solution file in pdf format",
                null=True,
                upload_to="online_submissions",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["pdf"]
                    )
                ],
                verbose_name="Solution file",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="onlinesubmission",
            unique_together={("user", "problem")},
        ),
    ]
