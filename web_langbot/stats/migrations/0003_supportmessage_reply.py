# Generated by Django 3.0.5 on 2020-04-29 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_supportmessage_message_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportmessage',
            name='reply',
            field=models.CharField(default='', max_length=3000),
        ),
    ]
