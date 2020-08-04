
import telebot

import markups

bot = telebot.TeleBot('removed:removed')


for i in ["65353297", ]:
    bot.send_message(int(i), "привет", reply_markup=markups.main_markup)

