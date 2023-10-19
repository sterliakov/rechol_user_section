# Generated by Django 4.0.5 on 2023-10-19 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0046_remove_venue_name_venue_full_name_venue_short_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfflineProblem',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('name', models.CharField(max_length=120, verbose_name='Name')),
                (
                    'file',
                    models.FileField(upload_to='problems', verbose_name='Statement'),
                ),
                (
                    'solution',
                    models.FileField(
                        null=True, upload_to='solutions', verbose_name='Solutions'
                    ),
                ),
                ('visible', models.BooleanField(default=False, verbose_name='Visible')),
                (
                    'target_form',
                    models.PositiveSmallIntegerField(
                        choices=[(8, '8'), (9, '9'), (10, '10'), (11, '11')],
                        default=8,
                        verbose_name='Target form',
                    ),
                ),
            ],
            options={
                'verbose_name': 'offline problem',
                'verbose_name_plural': 'offline problems',
            },
        ),
        migrations.AlterModelOptions(
            name='onlineproblem',
            options={
                'verbose_name': 'online problem',
                'verbose_name_plural': 'online problems',
            },
        ),
        migrations.AddField(
            model_name='configurationsingleton',
            name='show_offline_problems',
            field=models.BooleanField(
                default=False, verbose_name='allow downloading offline stage problems'
            ),
        ),
    ]
