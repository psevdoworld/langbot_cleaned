from datetime import datetime
from datetime import timedelta

import telebot
from django.utils.timezone import now

from DictionaryApp.models import UsersWord
from bot_users.models import BotUser


class AppUser:

    def __init__(self, tg_id):
        self.tg_id = tg_id
        self.bot_user = BotUser.objects.get(tg_id=tg_id)
        self.update_last_action()

    def word_to_repeat(self):
        last_word = UsersWord.objects.filter(bot_user=self.bot_user, learned=True).order_by("when_repeat").first()
        if last_word:
            if last_word.when_repeat.date() <= now().date():
                self.update_old_word(UsersWord.objects.filter(bot_user=self.bot_user, learned=True).order_by("when_repeat"))
                return last_word.word
        return None

    def change_repeat_word_status(self, word_id, mem_status):
        word = UsersWord.objects.filter(word__id=word_id, bot_user=self.bot_user).first()
        print(word, mem_status)
        if mem_status == "good":
            word.count_days = 2 * word.count_days + 1
            word.when_repeat = now() + timedelta(word.count_days)
            word.save()
        elif mem_status == "not_good":
            word.count_days = 1
            word.when_repeat = now() + timedelta(word.count_days)
            word.save()
        elif mem_status == "bad":
            word.count_days = 1
            word.when_repeat = now() + timedelta(minutes=10)
            word.save()

    @staticmethod
    def update_old_word(words):
        for word in words:
            if word.when_repeat.date() < now().date():
                word.when_repeat = now()
                word.save()

    def update_last_action(self):
        last_action_date = self.bot_user.last_action.date()
        if last_action_date != now().date() and last_action_date == now().date() - timedelta(1):
            self.bot_user.lifelong_learning += 1
            if self.bot_user.lifelong_learning % 5 == 0:
                days = self.bot_user.lifelong_learning
                self.add_rating(5, message=f"Ты занимешься уже {days} дней подряд. Держи заслуженные 5 ❤")
        elif last_action_date < now().date() - timedelta(1):
            self.bot_user.lifelong_learning = 0
        self.bot_user.last_action = now()
        self.bot_user.save()

    def stats(self):
        today = datetime.now().date()
        delta = timedelta
        data = {
            "rating": self.bot_user.rating,
            "count_words": UsersWord.objects.filter(bot_user=self.bot_user, learned=True).count(),
            "count_words_today": UsersWord.objects.filter(bot_user=self.bot_user, learned=True,
                                                          learned_date=today).count(),
            "count_words_week": UsersWord.objects.filter(bot_user=self.bot_user, learned=True,
                                                         learned_date__gt=today - delta(7)).count(),
            "lifelong_learning": self.bot_user.lifelong_learning,
        }
        return data

    def add_rating(self, count, message=None):
        self.bot_user.daily_rating += count
        self.bot_user.rating += count
        self.bot_user.save()
        if message:
            tb = telebot.TeleBot("1218756232:AAH8B9zQeZWS56IfW3_vIeiuc_YpU8s6D-w")
            ret_msg = tb.send_message(self.bot_user.tg_id, message, parse_mode="Markdown")

    def renew_subscription(self, amount):
        payment_d = {
            159: 30,
            299: 90,
            990: 365
        }
        if self.bot_user.allowed_date.date() <= datetime.now().date():
            self.bot_user.allowed_date = datetime.now().date() + timedelta(payment_d[int(amount)])
        else:
            self.bot_user.allowed_date += timedelta(payment_d[int(amount)])
        self.bot_user.save()
        tb = telebot.TeleBot("1218756232:AAH8B9zQeZWS56IfW3_vIeiuc_YpU8s6D-w")
        ret_msg = tb.send_message(self.bot_user.tg_id, "Подписка успешно проделена! ", parse_mode="Markdown")
