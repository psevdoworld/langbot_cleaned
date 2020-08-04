# Generated by Django 3.0.5 on 2020-04-23 10:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('DictionaryApp', '0004_auto_20200423_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersword',
            name='by_user',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='usersword',
            name='count_days',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='usersword',
            name='learned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='usersword',
            name='when_repeat',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]