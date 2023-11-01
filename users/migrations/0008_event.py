# Generated by Django 4.0.5 on 2022-10-03 18:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0007_alter_user_passport"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
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
                ("title", models.CharField(max_length=127, verbose_name="Title")),
                (
                    "link",
                    models.URLField(
                        help_text="Link to news page etc.", verbose_name="Link"
                    ),
                ),
                ("start", models.DateTimeField(verbose_name="Start")),
                ("description", models.TextField(verbose_name="Description")),
            ],
        ),
    ]
