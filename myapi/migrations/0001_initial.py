# Generated by Django 5.0.6 on 2024-06-25 13:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authtoken', '0004_alter_tokenproxy_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtendedToken',
            fields=[
                ('token_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='authtoken.token')),
                ('is_deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'extended_token',
            },
            bases=('authtoken.token',),
        ),
    ]