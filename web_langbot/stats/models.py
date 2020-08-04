from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.
from django.utils.timezone import now


class SupportMessage(models.Model):
    chat_id = models.IntegerField(verbose_name="Id чата")
    message_id = models.IntegerField(verbose_name="Id сообщения")
    text = models.CharField(max_length=3000, verbose_name="Текст сообщения")
    username = models.CharField(max_length=300, default="", verbose_name="Username")
    created = models.DateTimeField(default=now, verbose_name="Дата получения")
    message = JSONField()
    reply = models.CharField(max_length=3000, default="", verbose_name="Текст ответа")
    answered = models.BooleanField(default=False, verbose_name="Отвечено?")

    class Meta:
        verbose_name = "Сообщение поддержки"
        verbose_name_plural = "Сообщения поддержки"


class Mailing(models.Model):
    text = models.CharField(max_length=4000, verbose_name="Текст сообщения")
    created = models.DateTimeField(default=now, verbose_name="Дата создания")
    sended = models.DateTimeField(default=None, null=True, verbose_name="Дата рассылки")
    tested = models.BooleanField(default=False, verbose_name="Проверено?")
    count_received = models.IntegerField(default=0)
