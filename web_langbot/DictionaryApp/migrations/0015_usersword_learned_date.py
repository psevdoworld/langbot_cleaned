# Generated by Django 3.0.5 on 2020-04-30 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DictionaryApp', '0014_auto_20200430_0131'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersword',
            name='learned_date',
            field=models.DateField(default=None, null=True),
        ),
    ]
