# Generated by Django 3.0.5 on 2020-04-28 12:33

import bot_users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_users', '0007_botuser_ref_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='allowed_date',
            field=models.DateTimeField(default=bot_users.models.now_and_more),
        ),
    ]
