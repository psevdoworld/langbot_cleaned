# Generated by Django 3.0.5 on 2020-04-21 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_users', '0002_auto_20200421_1907'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botuser',
            name='id',
        ),
        migrations.AlterField(
            model_name='botuser',
            name='tg_id',
            field=models.IntegerField(db_index=True, primary_key=True, serialize=False, unique=True),
        ),
    ]
