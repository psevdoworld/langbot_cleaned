# Generated by Django 3.0.5 on 2020-04-23 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DictionaryApp', '0003_auto_20200421_1730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translation',
            name='audio',
            field=models.FileField(blank=True, null=True, upload_to='media/audio/'),
        ),
    ]
