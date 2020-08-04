import logging
import telebot
from django.utils.timezone import now

from bot_users.models import BotUser
from stats.models import Mailing
from web_langbot.celery import app
from web_langbot.settings import ADMINS_ID


@app.task
def send_spam(type_spam: str, mail_id):
    # tb = telebot.TeleBot("1118096811:AAFS6yfpzup4jtxdQ4GmpncwpZa64D2MrVE") # test
    tb = telebot.TeleBot("1218756232:AAH8B9zQeZWS56IfW3_vIeiuc_YpU8s6D-w")  # prod
    if type_spam == "test":
        mail = Mailing.objects.filter(id=mail_id).first()
        for id_ in ADMINS_ID:
            ret_msg = tb.send_message(id_, mail.text, parse_mode="Markdown")
        mail.tested = True
        mail.save()
    elif type_spam == "for_all":
        users = BotUser.objects.all()
        mail = Mailing.objects.filter(id=mail_id).first()

        for user in users:
            try:
                ret_msg = tb.send_message(user.tg_id, mail.text, parse_mode="Markdown")
                mail.count_received += 1
            except Exception as e:
                print(e)
        mail.sended = now()
        mail.save()
