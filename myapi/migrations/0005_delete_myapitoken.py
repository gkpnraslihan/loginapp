# Generated by Django 5.0.6 on 2024-06-26 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapi', '0004_rename_token_myapitoken'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MyapiToken',
        ),
    ]
