from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.
from django.utils.timezone import now

from bot_users.models import BotUser


class Transaction(models.Model):
    CREATED = 'CR'
    SUCCEEDED = 'SC'
    FAILED = 'FL'
    STATUS_CHOICES = [
        (CREATED, 'Создан'),
        (SUCCEEDED, 'Завершен'),
        (FAILED, 'Ошибка'),
    ]
    vnd = models.CharField(max_length=100, default="rbk")
    amount = models.IntegerField()
    bot_user = models.ForeignKey(BotUser, on_delete=models.deletion.SET)
    status = models.CharField(max_length=2,
                              null=False,
                              choices=STATUS_CHOICES,
                              default=CREATED,
                              verbose_name="Статус платежа")
    created = models.DateTimeField(default=now)
    closed = models.DateTimeField(default=None, null=True)
    request_data = JSONField(null=True)

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
