# Generated by Django 4.0.10 on 2023-11-10 14:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0054_alter_user_passport"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="onlineproblem",
            name="comment",
        ),
        migrations.AddField(
            model_name="offlineproblem",
            name="name_en",
            field=models.CharField(
                default="Problem set", max_length=120, verbose_name="Name (en)"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="onlineproblem",
            name="name_en",
            field=models.CharField(
                default="Problem set", max_length=120, verbose_name="Name (en)"
            ),
            preserve_default=False,
        ),
    ]
