# Generated by Django 4.0.5 on 2022-12-07 21:27

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0036_rename_file_onlinesubmission_paper_original'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='onlinesubmission',
            options={
                'verbose_name': 'Result (online)',
                'verbose_name_plural': 'Results (online)',
            },
        ),
        migrations.AddField(
            model_name='configurationsingleton',
            name='online_appeal_end',
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 14, 21, 0, tzinfo=utc),
                verbose_name='End of online stage appeal',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='configurationsingleton',
            name='online_appeal_start',
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 7, 21, 0, tzinfo=utc),
                verbose_name='Start of online stage appeal',
            ),
            preserve_default=False,
        ),
    ]