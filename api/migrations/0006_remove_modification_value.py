# Generated by Django 4.2 on 2023-06-06 15:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_modification_acquisition_year'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modification',
            name='value',
        ),
    ]
