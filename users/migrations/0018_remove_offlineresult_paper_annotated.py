# Generated by Django 4.0.5 on 2022-10-19 22:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_annotation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offlineresult',
            name='paper_annotated',
        ),
    ]
