from django.db import models
from django.contrib.postgres.fields import ArrayField
from datetime import datetime, timedelta, timezone, tzinfo
from django.utils.timezone import now
from django.conf import settings

from pytz import utc

LEVELS = {"начальный": "a1",
          "a1": "a2",
          "a2": "b1",
          "b1": "b2",
          "b2": "c1",
          "c1": "c1",
          }


def now_and_more():
    """
    Return an aware or naive datetime.datetime, depending on settings.USE_TZ.
    """
    if settings.USE_TZ:
        # timeit shows that datetime.now(tz=utc) is 24% slower
        date = datetime.utcnow().replace(tzinfo=utc)
    else:
        date = datetime.now()
    return date + timedelta(days=5)


class BotUser(models.Model):
    tg_id = models.IntegerField(null=False, db_index=True, unique=True, primary_key=True)
    first_name = models.CharField(max_length=250, null=True)
    username = models.CharField(max_length=250, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    notify_time = models.TimeField(null=True, verbose_name="Уведомления", blank=True)
    level = models.CharField(max_length=25, null=True, blank=True)
    ref_id = models.IntegerField(null=True, unique=False, blank=True)
    allowed_date = models.DateTimeField(default=now_and_more, verbose_name="Дата окончания подписки")
    last_action = models.DateTimeField(default=now, verbose_name="Последние действия")
    date_join = models.DateTimeField(default=now, verbose_name="Дата регистрации")
    lifelong_learning = models.IntegerField(default=0, verbose_name="Непрерывная серия")
    rating = models.IntegerField(default=0, verbose_name="Общий рейтинг")
    daily_rating = models.IntegerField(default=0, verbose_name="Днейвной рейтинг")

    class Meta:
        verbose_name = "Пользователь бота"
        verbose_name_plural = "Пользователи бота"

    def __str__(self):
        return f"{self.tg_id} + {self.username}"
