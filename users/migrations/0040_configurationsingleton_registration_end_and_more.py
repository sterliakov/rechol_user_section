# Generated by Django 4.0.5 on 2022-12-25 11:30

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0039_onlineproblem_solution'),
    ]

    operations = [
        migrations.AddField(
            model_name='configurationsingleton',
            name='registration_end',
            field=models.DateTimeField(
                default=datetime.datetime(2022, 9, 1, 0, 0),
                verbose_name='End of registration',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='configurationsingleton',
            name='registration_start',
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 24, 0, 0),
                verbose_name='Start of registration',
            ),
            preserve_default=False,
        ),
    ]