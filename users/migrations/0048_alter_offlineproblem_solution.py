# Generated by Django 4.0.5 on 2023-10-19 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0047_offlineproblem_alter_onlineproblem_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offlineproblem',
            name='solution',
            field=models.FileField(
                blank=True, null=True, upload_to='solutions', verbose_name='Solutions'
            ),
        ),
    ]
