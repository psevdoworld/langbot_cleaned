from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.timezone import now

from bot_users.models import BotUser


def jsonfield_default_value():  # This is a callable
    return {'tr': []}


class Topics(models.Model):
    name = models.CharField(db_index=True, max_length=250, unique=True)
    image = models.ImageField(upload_to='topic_img/', null=True)
    available = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Топик"
        verbose_name_plural = "Топики"

    def __str__(self):
        return self.name


class Translation(models.Model):
    lang_key = models.CharField(db_index=True, max_length=20, blank=True, default='end_rus')
    word = models.CharField(db_index=True, max_length=250)
    pos = models.CharField(max_length=250, blank=True)
    translation = JSONField(default=jsonfield_default_value)
    oxford_level = models.CharField(max_length=50, null=True,  blank=True)
    audio = models.FileField(upload_to='audio', blank=True, null=True)
    topics = models.ManyToManyField(Topics, blank=True, related_name='word_topic', db_table='word_topic')

    class Meta:
        unique_together = ('word', 'pos')
        verbose_name = "Слово"
        verbose_name_plural = "Слова"


class UsersWord(models.Model):
    bot_user = models.ForeignKey(BotUser, on_delete=models.CASCADE)
    word = models.ForeignKey(Translation, on_delete=models.CASCADE)
    by_user = models.BooleanField(default=False)
    learned = models.BooleanField(default=False)
    count_days = models.IntegerField(default=0)
    when_repeat = models.DateTimeField(default=now)
    learned_date = models.DateField(null=True, default=None)

    class Meta:
        unique_together = ('word', 'bot_user')
        verbose_name = "Слово пользователя"
        verbose_name_plural = "Слова пользователя"


class UsersTopic(models.Model):
    bot_user = models.ForeignKey(BotUser, on_delete=models.CASCADE)
    topics = models.ForeignKey(Topics, on_delete=models.CASCADE)


