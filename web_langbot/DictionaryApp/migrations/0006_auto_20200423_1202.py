# Generated by Django 3.0.5 on 2020-04-23 12:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot_users', '0004_botuser_words_to_learn'),
        ('DictionaryApp', '0005_auto_20200423_1040'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usersword',
            unique_together={('word', 'bot_user')},
        ),
    ]
