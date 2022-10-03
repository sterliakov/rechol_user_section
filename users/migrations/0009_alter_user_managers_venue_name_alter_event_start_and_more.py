# Generated by Django 4.0.5 on 2022-10-03 22:01

from django.db import migrations, models

import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_event'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', users.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='venue',
            name='name',
            field=models.CharField(default='Foo', max_length=63, verbose_name='Name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='start',
            field=models.DateTimeField(null=True, verbose_name='Start'),
        ),
        migrations.AlterField(
            model_name='user',
            name='actual_form',
            field=models.PositiveSmallIntegerField(
                choices=[(8, '8'), (9, '9'), (10, '10'), (11, '11'), (1, 'Other')],
                verbose_name='Actual form',
            ),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=127, verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=127, verbose_name='Last name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='participation_form',
            field=models.PositiveSmallIntegerField(
                choices=[(8, '8'), (9, '9'), (10, '10'), (11, '11')],
                verbose_name='Participation form',
            ),
        ),
        migrations.AlterField(
            model_name='user',
            name='patronymic_name',
            field=models.CharField(
                blank=True, default='', max_length=127, verbose_name='Patronymic name'
            ),
        ),
        migrations.AlterField(
            model_name='user',
            name='school',
            field=models.CharField(max_length=255, verbose_name='School'),
        ),
        migrations.AlterField(
            model_name='user',
            name='telegram_nickname',
            field=models.CharField(
                blank=True, default='', max_length=127, verbose_name='Telegram nickname'
            ),
        ),
    ]