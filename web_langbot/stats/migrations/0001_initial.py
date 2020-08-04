# Generated by Django 3.0.5 on 2020-04-29 22:31

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SupportMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.IntegerField()),
                ('text', models.CharField(max_length=3000)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('message', django.contrib.postgres.fields.jsonb.JSONField()),
                ('answered', models.BooleanField(default=False)),
            ],
        ),
    ]