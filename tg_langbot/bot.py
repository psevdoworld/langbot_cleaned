# coding=utf-8
import logging
import random
import sys
import re
import telebot
from multiprocessing import Process
import time, pytz
import os
from datetime import datetime

from rest_framework.utils import json
from telebot import types, util

from Api import Api, get_tg_link, get_public_link, set_bot_name, detect
from Game import GameApi
from Talk import Talk
from somewhere import newtest43_token, test_robin_bot_token, dev_ids
import markups
from BackendApi import LangBotApi
from Learn import LearnWords, pos_dict, Topics, TestLevel, levels_str
from text_messages import exampel_mesage, message_text
from Users import Users, UsersDict, UsersRepeat

try:
    dev_bot = telebot.TeleBot("removed:removed", threaded=True, skip_pending=False,
                              num_threads=4)
except Exception as e:
    print("TESTBOT FAILED TO START\n" * 5)
    print(e)
regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
if 1:
    set_bot_name("newtest43_bot")
    token = newtest43_token
else:
    set_bot_name("test_robin_bot")
    token = test_robin_bot_token
if os.environ.get('BOT_TOKEN'):
    set_bot_name("TeachEnglish_bot")
token = os.environ.get('BOT_TOKEN') or token
success = False
while not success:
    try:
        bot = telebot.TeleBot(token, threaded=True, skip_pending=False, num_threads=4)
        success = True
    except Exception as e:
        print(e)
        print("creating telebot")
        time.sleep(3)
telebot.logger.setLevel(logging.ERROR)
success = False
try:
    for i in dev_ids:
        dev_bot.send_message(int(i), "привет", reply_markup=markups.main_markup)
        success = True
except Exception as e:
    print("cant reach to my masters :'(\n" * 5)
    print(e)
    time.sleep(3)

users = Users()
repeat_words = UsersRepeat()
talk = Talk(bot, users)


def log_inline(call):
    #     LangBotApi.call_log(call)
    pass


#
#
def log_messages(messages):
    pass


#     for message in messages:
#         LangBotApi.message_log(message)
#         pass


bot.set_update_listener(log_messages)


def bot_send_message_safe(*args, **kwargs):
    try:
        bot.send_message(*args, **kwargs)
    except Exception as e:
        print(e)
        print("bot_send_message_safe failed\n" * 5)
        print(args)
        print(kwargs)
        try:
            for i in dev_ids:
                dev_bot.send_message(i, e, reply_markup=markups.main_markup)
        except Exception as e:
            print("bot_send_message_safe failed and dev bot failed also")
            print(e)

def bot_delete_message_safe(*args, **kwargs):
    try:
        bot.delete_message(*args, **kwargs)
    except Exception as e:
        print(e)
        print("def bot_delete_message_safe(*args, **kwargs): failed\n" * 5)
        print(args)
        print(kwargs)
        try:
            for i in dev_ids:
                dev_bot.send_message(i, e, reply_markup=markups.main_markup)
        except Exception as e:
            print("def bot_delete_message_safe(*args, **kwargs): failed and dev bot failed also")
            print(e)


def check_send_messages():
    while True:
        try:
            now = datetime.now()
            next_hour = datetime.now().replace(microsecond=0, second=59, minute=59)  # каждый час
            # next_hour = datetime.now().replace(microsecond=0, second=59)  # каждая минута

            wait_seconds = (next_hour - now).seconds + 4.2
            # wait_seconds =  1.2
            time.sleep(wait_seconds)
            while (datetime.now().minute > 30):
                now = datetime.now()
                next_hour = datetime.now().replace(microsecond=0, second=59, minute=59)  # каждый час
                # next_hour = datetime.now().replace(microsecond=0, second=59)  # каждая минута

                wait_seconds = (next_hour - now).seconds + 4.2
                # wait_seconds =  1.2
                time.sleep(wait_seconds)
            time_utc = pytz.utc.localize(datetime.utcnow())
            time_msk = time_utc.astimezone(pytz.timezone("Europe/Moscow"))
            print(time_msk.time())
            users = LangBotApi.get_users_by_time_notify(str(time_msk.time())[:4] + "0:00")
            # users = LangBotApi.get_users_by_time_notify(str(datetime.now().time())[:5]+":00")
            # print(users[0])
            if users:
                for i in users:
                    name = i["first_name"] or i["username"] or " Привет"
                    bot_send_message_safe(i["tg_id"], f"{name}🥳, пора продолжить учиться)",
                                          reply_markup=markups.main_markup)
            try:
                for i in dev_ids:
                    dev_bot.send_message(i, time_msk, reply_markup=markups.main_markup)
            except Exception as e:
                print("TESTBOT FAILED")
                print(e)

        except Exception as e:
            print(e)


p1 = Process(target=check_send_messages, args=())
p1.start()


def stop_old_games():
    while True:
        try:
            # print(42)
            time.sleep(5)
            results = GameApi.exit_games_if_its_time()
            if results:
                for data in results:
                    do_game_results(data)
        except Exception as e:
            print(e)


p2 = Process(target=stop_old_games, args=())
p2.start()


def is_allowed_or_msg(chat_id):
    if Api().is_allowed_today(chat_id):
        return True
    else:
        users.set_state(chat_id, "cabinet")
        bot_send_message_safe(chat_id,
                              """🤭Извини
Эта функция работает только в платной версии бота...

*🥳всего за 3 рубля в день*, все функции будут работать без ограничений)""",
                              reply_markup=markups.cabinet_markup, parse_mode="Markdown")
        return False


def is_call_legal(call):  # legalised
    return True
    legal_actions_for_state = {"init": "share_link" in call.data,
                               "test_started": call.data[:3] in ("goo", "bad"),
                               "learning_word": ("goto" in call.data[:4] or
                                                 "more" in call.data[:4] or
                                                 "start_quiz" in call.data),
                               "search_word": ("add" in call.data or
                                               "menu" in call.data or
                                               "fuck_go_back" in call.data),
                               "add_translate": ("add" in call.data or
                                                 "menu" in call.data or
                                                 "fuck_go_back" in call.data),
                               "quiz": ("good" in call.data[:4] or
                                        "bad" in call.data[:3] or
                                        "next" in call.data[:4]),
                               "my_dict": "goto" in call.data,
                               "playing_game": call.data in ("good_game", "bad_game"),
                               "learn": ("learn_my_words" in call.data or
                                         "start_test" in call.data),
                               "interval_repeat": ("start_interval_repeat" in call.data or
                                                   "open_card" in call.data or
                                                   call.data in ("bad", "not_good", "good")),

                               }

    state = users.get_state(call.from_user)
    if state not in legal_actions_for_state:
        print(state, "is not registeret as legal!!!!!")
        return True
    else:
        return legal_actions_for_state[state]


@bot.callback_query_handler(func=lambda call: not is_call_legal(call))
def callback_inline(call):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Работа с этим сообщением сейчас недоступна.", parse_mode="Markdown",
                          reply_markup=None)


@bot.chosen_inline_handler(func=lambda chosen_inline_result: chosen_inline_result.query == "game_invite")
def choose_game_topic(chosen_inline_result):
    GameApi.new_game_invite(chosen_inline_result.from_user.id, chosen_inline_result.result_id)


@bot.inline_handler(lambda query: query.query == "game_invite")
def query_photo(inline_query):
    if LangBotApi.get_user(inline_query.from_user.id):
        try:
            bot.answer_inline_query(inline_query.id, Topics().get_topics(user_id=inline_query.from_user.id),
                                    cache_time=1)
        except Exception as e:
            print(e)
    else:
        print("inline pidor", inline_query.from_user.id)
        return


@bot.chosen_inline_handler(func=lambda chosen_inline_result: chosen_inline_result.query == "topic")
def test_chosen(chosen_inline_result):
    data = LangBotApi.get_words_for_learn(chosen_inline_result.from_user.id, chosen_inline_result.result_id)
    if data == 'Вы выучили все слова в этом топике!':
        bot_send_message_safe(chosen_inline_result.from_user.id,
                              'Вы выучили все слова в этом топике!',
                              reply_markup=markups.main_markup)
        return
    learn_word_now(chosen_inline_result.from_user.id, topic_id=chosen_inline_result.result_id)


@bot.inline_handler(lambda query: query.query == "topic")
def query_photo(inline_query):
    print(inline_query.query)
    if LangBotApi.get_user(inline_query.from_user.id):
        try:
            bot.answer_inline_query(inline_query.id, Topics().get_topics(), cache_time=1)
        except Exception as e:
            print(e)
    else:
        print("inline pidor on topic\n"*2, inline_query.from_user.id)
        return

@bot.message_handler(func=lambda message: message.from_user.id != message.chat.id)
def text_message(message):
    print("popalsa pidor!\n" * 10)
    try:
        bot_send_message_safe(message.chat.id, "Простите, на данный момент группы не поддерживаются",
                              reply_markup=None)
        bot.leave_chat(message.chat.id)
    except Exception as e:
        print("popalsa pidor!\n" * 10)
        print("cant leave!\n" * 10)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    is_game = False
    ref_id = message.text.split(" ")[1] if " " in message.text else None
    # users.get_state(message.from_user, ref_id=ref_id)  # не ломать - рефералка
    # users.get_state(message.from_user, ref_id=ref_id) # не ломать - рефералка
    if ref_id is not None and "g" in ref_id:
        is_game = True
        ref_id = int(ref_id.lstrip("g"))
    # print(1, users.get_state(message.from_user))
    # print(users.get_state(message.from_user) == "email" and not is_game)
    if (users.get_state(message.from_user, ref_id=ref_id) == "email") and (not is_game):
        bot_send_message_safe(message.chat.id, "🔥Для успешной регистрации просто напишите свой E-mail",
                              reply_markup=markups.hideBoard)
        print(2, users.get_state(message.from_user))
        return

    users.reset_state(message.chat.id)

    if not is_game:
        bot_send_message_safe(message.chat.id, "Привет 😉",
                              reply_markup=markups.main_markup)
    # bot.send_message(message.chat.id, "здесь будет предложение обучения для знакомства с фичами",
    #                  reply_markup=markups.main_markup)

    topic = GameApi.accept_invite(ref_id, message.from_user.id)

    if is_game and topic is not None:
        if ref_id == message.from_user.id:
            bot_send_message_safe(message.chat.id, "Вам не обязательно переходить по этой ссылке, она для оппонента.",
                                  reply_markup=markups.main_markup)
            return
        print(message.chat.id, message.from_user.id)
        GameApi.start_game(ref_id, message.from_user.id)
        ref_user = LangBotApi.get_user(ref_id)
        user_user = LangBotApi.get_user(message.from_user.id)
        try:
            if not (ref_user and user_user):
                print("WTF\n" * 10)
                print(ref_user, user_user)
                print(topic)
                print(ref_id, message.from_user.id)
                bot_send_message_safe(ref_id, "Это приглашение к игре недействительно",
                                      reply_markup=markups.main_markup)
                bot_send_message_safe(message.from_user.id, "Это приглашение к игре недействительно",
                                      reply_markup=markups.main_markup)
                return
        except Exception as e:

            print(e)
        start_game(ref_id)
        start_game(message.from_user.id)

    elif is_game and topic is None:
        bot_send_message_safe(message.chat.id, "Это приглашение к игре недействительно",
                              reply_markup=markups.main_markup)


@bot.message_handler(commands=['test'])
def text_message(message):
    for i in ("test message", None, "message after illegal one"):
        bot_send_message_safe(message.chat.id,
                              i,
                              reply_markup=markups.main_markup)


@bot.message_handler(content_types=["text"], func=lambda message: users.get_state(message.from_user) == "email")
def text_message(message):
    if re.search(regex, message.text):
        LangBotApi.add_email_user(message.chat.id, message.text)
        users.reset_state(message.chat.id)
        bot_send_message_safe(message.chat.id,
                              "💪🏻Поздравляю, через 5 минут обучения с ботом, ты поймёшь, что это было правильное решение!",
                              reply_markup=markups.main_markup)
        photo = open('open_menu.jpg', 'rb')
        bot.send_photo(message.chat.id,
                       photo,
                       reply_markup=markups.main_markup)
    else:
        bot_send_message_safe(message.chat.id,
                              "👍Для успешной регистрации введите *корректный* Email", parse_mode="Markdown")


@bot.message_handler(content_types=["text"], func=lambda message: users.get_state(message.from_user) == "search_word")
def text_message(message):
    translate_word(message)


###################################################################
# Talk Handler
@bot.message_handler(commands=['stop_talk'])
def stop_talk(message):
    talk.stop_talking(message.chat.id)


@bot.message_handler(content_types=["text"], func=lambda message: users.get_state(message.from_user) == "wait_talk")
def talk_message_message(message):
    if "Я устал болтать" in message.text:
        talk.stop_wait(message.chat.id)
    else:
        bot_send_message_safe(message.chat.id,
                              "Собеседниек пока не найден, подожди немного или нажми *Я устал болтать*",
                              reply_markup=markups.stop_talk_murkup, parse_mode="Markdown")


@bot.message_handler(content_types=["text"], func=lambda message: users.get_state(message.from_user) == "talking")
def talk_message(message):
    if "Я устал болтать" in message.text:
        talk.stop_talking(message.chat.id)
    elif message.text in markups.button_list or "Пора бы" in message.text:
        bot_send_message_safe(message.chat.id,
                              "Чтобы прекратить диалог нажми *Я устал болтать*.\n  Чтобы продолжить открой клавиатуру.",
                              reply_markup=markups.stop_talk_murkup, parse_mode="Markdown")
        photo = open('open_keyboard.jpg', 'rb')
        bot.send_photo(message.chat.id,
                       photo)
    else:
        talk.redirect_message(message.chat.id, message.text)


@bot.callback_query_handler(func=lambda call: users.get_state(call.from_user) == "wait_talk")
def talk_callback_inline(call):
    log_inline(call)
    if "talk_stop" in call.data:
        talk.stop_wait(call.message.chat.id)


@bot.message_handler(content_types=["text"], func=lambda message: users.get_state(message.from_user) == "pay")
def pay_message(message):
    if message.text == "Назад в меню":
        users.reset_state(message.chat.id)
        bot_send_message_safe(message.chat.id, "Чем займемся?",
                              reply_markup=markups.main_markup)
    elif "-" in message.text:
        users.reset_state(message.chat.id)
        url = LangBotApi.get_pay_link(message.chat.id, message.text.split("-")[1].split()[0])
        print(url)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Оплатить подписку", url=url, callback_data="to_pay"))
        bot_send_message_safe(message.chat.id, f"К оплате {message.text} руб.",
                              reply_markup=keyboard)
    else:
        dont_understand(message)


@bot.message_handler(content_types=["text"],
                     func=lambda message: users.get_state(message.from_user) == "support")
def support_message(message):
    users.reset_state(message.chat.id)
    LangBotApi.support_message(message)
    bot_send_message_safe(message.chat.id, message_text['support_2'],
                          reply_markup=markups.main_markup)


@bot.message_handler(content_types=["text"], func=lambda message: users.get_state(message.from_user) == "add_translate")
def text_message(message):
    if is_allowed_or_msg(message.chat.id):
        add_translate(message)


@bot.message_handler(content_types=["text"], func=lambda message: users.get_state(message.from_user) == "time_notify")
def text_message(message):
    if message.text == "Назад в меню":
        users.reset_state(message.chat.id)
        bot_send_message_safe(message.chat.id, "Чем займемся?",
                              reply_markup=markups.main_markup)
    elif message.text == "Отключить уведомления":

        users.reset_state(message.chat.id)
        users.edit_notify(message.chat.id, None)
        bot_send_message_safe(message.chat.id, "Хорошо, напоминания отключены",
                              reply_markup=markups.main_markup)
    elif message.text in ('9:00', '12:00', '13:00', '14:00', '18:00', '19:00', '20:00', '21:00', '22:00'):
        users.edit_notify(message.chat.id, message.text)
        users.reset_state(message.chat.id)
        bot_send_message_safe(message.chat.id, "Отлично! В это время я буду напоминать тебе поучить слова.",
                              reply_markup=markups.main_markup)
    else:
        dont_understand(message, markups.time_notify_markup)


@bot.message_handler(content_types=["text"])
def text_message(message):
    state = users.get_state(message.from_user)
    print(state, message.chat.id)
    if message.text in ["Меню", "🤳Меню", "Закончить обучение", "Назад в меню"]:
        users.reset_state(message.chat.id)
        bot_send_message_safe(message.chat.id, "Чем займемся?", reply_markup=markups.main_markup)
    elif state == "init":
        main_message(message)
    elif state in ("learn", "my_dict", "search_word"):
        users.set_state(message.chat.id, "learn")
        learn_message(message)
    elif state == "cabinet":
        cabinet_message(message)
    else:
        dont_understand(message)


@bot.callback_query_handler(func=lambda call: users.get_state(call.from_user) == "init")
def callback_inline(call):  # legalised
    log_inline(call)

    if "share_link" in call.data:
        bot_send_message_safe(call.message.chat.id, get_public_link(call.message.chat.id),
                              disable_web_page_preview=True, reply_markup=markups.main_markup)


@bot.callback_query_handler(func=lambda call: users.get_state(call.from_user) == "test_started")
def callback_inline(call):
    log_inline(call)
    if call.data[:3] in ("goo", "bad"):  # не опечатка
        answer = " ".join(call.data.split(" ")[1:])
        # LangBotApi.change_word_status(call.message.chat.id, answer)
        data = TestLevel().test_answer(call.message.chat.id, good=("good" in call.data[:4]))
        if "ест завершен" in data["text"]:
            users.reset_state(call.message.from_user)
            try:
                bot_delete_message_safe(call.message.chat.id, call.message.message_id)
            except Exception as e:
                print("cant delete\n" * 5)
                print(e)
            bot_send_message_safe(call.message.chat.id, data["text"], reply_markup=markups.main_markup)
            users.reset_state(call.message.chat.id)
            return
        try:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=data["text"], parse_mode="Markdown",
                                  reply_markup=data["keyboard"])
        except Exception as e:
            print("cant edit\n" * 5)
            print(e)


@bot.callback_query_handler(func=lambda call: users.get_state(call.from_user) == "learning_word")
def callback_inline(call):
    log_inline(call)
    if "goto" in call.data[:4] or "more" in call.data[:4]:
        word_number = call.data.split(" ")[1]
        data = LearnWords().get_word_keys_data(call.message.chat.id, word_number, more=("more" in call.data[:4]))
        # keyboard = telebot.types.InlineKeyboardMarkup()
        # buttons = [telebot.types.InlineKeyboardButton(text="asdasdad", callback_data="gohgghd")]
        # keyboard.add(*buttons)

        bot_delete_message_safe(call.message.chat.id, call.message.message_id)
        bot.send_voice(call.message.chat.id,
                       data["audio"],
                       data["text"],
                       reply_markup=data["keyboard"],
                       duration=2,
                       disable_notification=True, parse_mode="Markdown")

    elif "start_quiz" in call.data:
        users.set_state(call.message.chat.id, "quiz")
        data = LearnWords().check_memorized(call.message.chat.id)
        bot_delete_message_safe(call.message.chat.id, call.message.message_id)
        bot_send_message_safe(call.message.chat.id, "Отлично, давай начнем", reply_markup=markups.end_learn_murkup)
        bot_send_message_safe(call.message.chat.id, data["text"], parse_mode="Markdown", disable_web_page_preview=True,
                              reply_markup=data["keyboard"])


@bot.callback_query_handler(func=lambda call: users.get_state(call.from_user) in ("search_word", "add_translate"))
def callback_inline(call):
    log_inline(call)
    if "add" in call.data:
        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text="Добавлено", callback_data="add"),
                   types.InlineKeyboardButton(text="вернуться в меню", callback_data="menu"),
                   ]
        keyboard.add(*buttons)
        if len(call.data.split()) > 1:
            LangBotApi.add_world_user(call.message.chat.id, call.data.split()[1])
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=call.message.text, parse_mode="Markdown",
                              reply_markup=keyboard)

    elif "menu" in call.data:
        users.reset_state(call.message.chat.id)
        bot_send_message_safe(call.message.chat.id, "Чем займемся?", reply_markup=markups.main_markup)

    elif "fuck_go_back" in call.data:
        users.set_state(call.message.chat.id, "learn")
        bot_send_message_safe(call.message.chat.id, "Чем теперь займемся?", reply_markup=markups.learn_markup)


@bot.callback_query_handler(func=lambda call: users.get_state(call.from_user) == "quiz")
def callback_inline(call):
    log_inline(call)
    if "good" in call.data[:4]:
        answer = " ".join(call.data.split(" ")[1:])
        LangBotApi.change_word_status(call.message.chat.id, answer)
        data = LearnWords().good_answer(call.message.chat.id)
        if "слов завершенно" in data["text"]:
            users.reset_state(call.message.from_user)
            bot_send_message_safe(call.message.chat.id, "Чем теперь займемся?", reply_markup=markups.main_markup)
            users.reset_state(call.message.chat.id)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=data["text"], parse_mode="Markdown",
                              reply_markup=data["keyboard"])
    elif "bad" in call.data[:3]:
        data = LearnWords().bad_answer(call.message.chat.id)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=data["text"], parse_mode="Markdown",
                              reply_markup=data["keyboard"])
    elif "next" in call.data[:4]:
        data = LearnWords().next_answer(call.message.chat.id)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=data["text"], parse_mode="Markdown",
                              reply_markup=data["keyboard"])


@bot.callback_query_handler(func=lambda call: users.get_state(call.from_user) == "my_dict")
def callback_inline_my_dict(call):
    log_inline(call)
    if "goto" in call.data:
        page = int(call.data.split()[1])
        text, keyboard = UsersDict().get_user_dict(call.message.chat.id, page=page)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text, parse_mode="Markdown",
                              reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: users.get_state(call.from_user) == "playing_game")
def callback_inline_my_dict(call):
    log_inline(call)
    if call.data in ("good_game", "bad_game"):
        data = GameApi.get_next_step(call.message.chat.id, call.data == "good_game")
        if "Вы ответили на все вопросы!\n Ждем вашего оппонента для подведения итогов." != data["text"]:

            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=data["text"], parse_mode="Markdown",
                                  reply_markup=data["keyboard"])
        else:
            bot_delete_message_safe(call.message.chat.id, call.message.message_id)
            bot_send_message_safe(call.message.chat.id, data["text"], reply_markup=data["keyboard"])
            users.reset_state(call.message.chat.id)
        if data["results"] is not None:
            do_game_results(data["results"])


@bot.callback_query_handler(func=lambda call: users.get_state(call.from_user) == "learn")
def callback_inline_my_dict(call):
    log_inline(call)
    if "learn_my_words" in call.data:
        learn_word_now(call.message.chat.id)

    if "start_test" in call.data:
        if is_allowed_or_msg(call.message.chat.id):
            data = Api().start_new_test(call.message.chat.id)
            if data is not None:
                users.set_state(call.message.chat.id, "test_started")
                # data = LearnWords().check_memorized(call.message.chat.id)
                data = TestLevel().test_question_data(call.message.chat.id)
                # bot.delete_message(call.message.chat.id, call.message.message_id)
                bot_send_message_safe(call.message.chat.id, "Отлично, тест на уровень начат",
                                      reply_markup=markups.end_test_murkup)
                bot_send_message_safe(call.message.chat.id, data["text"], parse_mode="Markdown",
                                      disable_web_page_preview=True,
                                      reply_markup=data["keyboard"])
            else:
                bot_send_message_safe(call.message.chat.id,
                                      "У нас нет новых тестов для вас. Самое время посоревноваться с друзьями! ❤",
                                      reply_markup=markups.learn_markup)


@bot.callback_query_handler(func=lambda call: users.get_state(call.from_user) == "interval_repeat")
def callback_inline_my_dict(call):
    log_inline(call)
    # print(call)
    if "start_interval_repeat" in call.data:
        text, keyboard = repeat_words.get_word_to_repeat(call.message.chat.id)
        print(text)
        if "нет слов" in text:
            users.set_state(call.message.chat.id, "learn")
        bot_send_message_safe(call.message.chat.id, text, parse_mode="Markdown", reply_markup=keyboard)
    elif "open_card" in call.data:
        text, keyboard = repeat_words.open_card(call.message.chat.id)
        if text and keyboard:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=text, parse_mode="Markdown",
                                  reply_markup=keyboard)
    elif call.data in ("bad", "not_good", "good"):
        text, keyboard = repeat_words.next_word(call.message.chat.id, call.data)
        if "нет слов" in text:
            users.set_state(call.message.chat.id, "learn")
            keyboard = types.InlineKeyboardMarkup()
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text, parse_mode="Markdown",
                              reply_markup=keyboard)


def main_message(message):
    if "Учиться" in message.text:
        users.set_state(message.chat.id, "learn")
        bot_send_message_safe(message.chat.id, message_text["start_learn"],
                              reply_markup=markups.learn_markup, parse_mode="Markdown")

    elif "Выбрана тема" in message.text:
        pass

    elif "Игры" in message.text:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Выбрать оппонента", switch_inline_query="game_invite"))
        bot_send_message_safe(message.chat.id, "Выберите оппонента, а затем и топик, чтобы начать сражение",
                              reply_markup=keyboard)

    elif "Болталка" in message.text:
        if is_allowed_or_msg(message.chat.id):
            flag = talk.new_talking(message.chat.id)
            if not flag:
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text="Устал ждать", callback_data="talk_stop"))
                bot_send_message_safe(message.chat.id, message_text["talk_message"], reply_markup=keyboard,
                                      parse_mode="Markdown")

    elif "Мой Прогресс" in message.text:
        # keyboard = types.InlineKeyboardMarkup()
        # keyboard.add(types.InlineKeyboardButton(text="Пройти тест", callback_data="start_test"))
        if is_allowed_or_msg(message.chat.id):
            stat_text = users.get_progress(message.chat.id)
            level = Api().get_current_level(message.chat.id)
            text = stat_text + "\n\n*Ваш текущий уровень:* " + levels_str[
                level]  # + ".\nВы можете поднять уровень, пройдя тест."
            bot_send_message_safe(message.chat.id, text, reply_markup=markups.main_markup, parse_mode="Markdown")
        else:
            return

    elif "Общий рейтинг" in message.text:
        data = LangBotApi.general_rating()
        text = "*Топ пользователей за все время\n*"
        for index, user in enumerate(data):
            temp = f"\n {index + 1}. {user[0]} - {user[1]} ❤".replace('_', '\\_').replace('*', '\\*')
            text += temp
        data = LangBotApi.general_daily_rating()
        text += "\n\n*Топ пользователей за сегодня*\n"
        for index, user in enumerate(data):
            temp = f"\n {index + 1}. {user[0]} - {user[1]} ❤".replace('_', '\\_').replace('*', '\\*')
            text += temp
        bot_send_message_safe(message.chat.id, text, reply_markup=markups.main_markup, parse_mode="Markdown", )

    elif "Расписание" in message.text:
        bot_send_message_safe(message.chat.id, message_text["choose_notify"],
                              reply_markup=markups.time_notify_markup)
        users.set_state(message.chat.id, "time_notify")

    elif "Пригласить" in message.text:
        days, end_date = Api().get_allowed_days_date(message.chat.id)
        days = 0 if days < 0 else days
        refs = LangBotApi.get_user_referals_count(message.chat.id)
        text = f"""
*Дней осталось:* {days}
Ты можешь учиться бесплатно, привлекая новых пользователей!

Для этого размещай свою ссылку и делись с друзьями и знакомыми

За каждого пользователя тебе будут начисляться 5 дней пользования ботом без ограничений
Когда твой друг пригласит нового друга, ты получишь + 1 день в подарок 

*Ты привел:* {refs[0]} пользователей
*Твои друзья привели:* {refs[1]} пользователей

Пригласите друзей по кнопкам ниже
"""

        bot_send_message_safe(message.chat.id, text,
                              reply_markup=markups.get_referal_markup(message.chat.id), parse_mode="Markdown")
        # users.set_state(message.chat.id, "referal")
    elif "Личный кабинет" in message.text:
        users.set_state(message.chat.id, "cabinet")
        days, end_date = Api().get_allowed_days_date(message.from_user.id)
        days = 0 if days < 0 else days
        bot_send_message_safe(message.chat.id, f"\n*Твой баланс:* {days} дней",
                              reply_markup=markups.cabinet_markup, parse_mode="Markdown")
    else:
        dont_understand(message)


def learn_message(message):
    if "Изучать слова" in message.text:
        text = message_text["learn_word"]
        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text="Слова из базы", callback_data="learn_my_words")]
        buttons += [types.InlineKeyboardButton(text="Выбрать тему", switch_inline_query_current_chat="topic")]
        keyboard.add(buttons[0])
        keyboard.add(buttons[1])
        bot_send_message_safe(message.chat.id, text, reply_markup=keyboard, parse_mode="Markdown")

    elif "Повторить слова" in message.text:
        bot_send_message_safe(message.chat.id, "Повторение слов", reply_markup=markups.learn_markup)

    elif "Перевести слово" in message.text:
        if is_allowed_or_msg(message.chat.id):
            bot_send_message_safe(message.chat.id, message_text["translate"], reply_markup=types.ReplyKeyboardRemove(),
                                  parse_mode="Markdown")
            users.set_state(message.chat.id, "search_word")

    elif "Мой словарь" in message.text:
        users.set_state(message.chat.id, "my_dict")
        text, keyboard = UsersDict().get_user_dict(message.chat.id)
        bot_send_message_safe(message.chat.id, message_text["my_dict"], reply_markup=markups.learn_markup,
                              parse_mode="Markdown")
        bot_send_message_safe(message.chat.id, text, reply_markup=keyboard, parse_mode="Markdown")

    elif "Интервальное повторение" in message.text:
        if True or is_allowed_or_msg(message.chat.id):
            users.set_state(message.chat.id, "interval_repeat")
            text, keyboard = repeat_words.get_word_to_repeat(message.chat.id)
            bot.send_photo(message.chat.id,
                           "https://commons.wikimedia.org/wiki/File:Leitner_system_alternative.svg?uselang=ru",
                           reply_markup=markups.end_learn_murkup)
            keyboard = types.InlineKeyboardMarkup()
            buttons = types.InlineKeyboardButton(text="Понятно, перейти к повторению",
                                                 callback_data="start_interval_repeat")
            keyboard.add(buttons)
            bot_send_message_safe(message.chat.id, message_text["interval_repeat"],
                                  parse_mode="Markdown",
                                  disable_web_page_preview=True,
                                  reply_markup=keyboard)

    elif "Учить мои слова" in message.text:
        learn_word_now(message.chat.id)

    elif "Расписание" in message.text:
        bot_send_message_safe(message.chat.id, message_text["choose_notify"], reply_markup=markups.time_notify_markup)
        users.set_state(message.chat.id, "time_notify")
    elif "Меню" in message.text:
        users.reset_state(message.chat.id)
        bot_send_message_safe(message.chat.id, "Чем займемся?", reply_markup=markups.main_markup)
    elif "Проверить уровень" in message.text:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Пройти тест", callback_data="start_test"))
        level = Api().get_current_level(message.chat.id)
        text = "*Ваш текущий уровень:* " + levels_str[level] + ".\nВы можете поднять уровень, пройдя тест."
        bot_send_message_safe(message.chat.id, text, reply_markup=keyboard, parse_mode="Markdown")
    elif "Выбрана тема" in message.text:
        print("")
    else:
        dont_understand(message, markups.learn_markup)


def cabinet_message(message):
    if "Оплата" in message.text:
        users.set_state(message.chat.id, "pay")
        days, end_date = Api().get_allowed_days_date(message.chat.id)
        days = 0 if days < 0 else days
        text = f"*💰Твой баланс:* {days} дней"
        text += "\n" + message_text["pay"]
        bot_send_message_safe(message.chat.id, text,
                              reply_markup=markups.pay_markup, parse_mode="Markdown")
    elif "Поддержка" in message.text:
        users.set_state(message.chat.id, "support")
        bot_send_message_safe(message.chat.id, message_text['support_1'], reply_markup=markups.hideBoard)
    else:
        dont_understand(message, markups.cabinet_markup)


def add_translate(message):
    # users.set_state(message.chat.id, "learn")
    if "-" in message.text:
        word = message.text.split("-")[0].rstrip()
        if detect(word) != "en":
            # bot.send_message(message.chat.id, "Неверный язык", reply_markup=markups.add_word_tr_markup)
            # return
            word = message.text.split("-")[1].lstrip()
            trans = [message.text.split("-")[0].rstrip()]
        else:
            trans = [trs.rstrip().lstrip() for trs in message.text.split("-")[1].lstrip().split(",")]
        data = LangBotApi.add_translate_word(word, trans)
        translate_word(message, data)
    else:
        bot_send_message_safe(message.chat.id, "Неправильный формат", reply_markup=markups.add_word_tr_markup)


def translate_word(message, user_added_data=None):
    if user_added_data is None:
        words = LangBotApi.get_word_translate(message.text)
    else:
        words = user_added_data
    if not words:
        users.set_state(message.chat.id, "learn")
        text = "🤭 Мы не смогли перевести это слово, но ты можешь добавить сейчас перевод и мы добавим его в базу"
        text += "\n 🔹 Используй следующий формат:\n *слово - перевод*"
        bot_send_message_safe(message.chat.id, text, reply_markup=markups.add_word_tr_markup, parse_mode="Markdown")
        users.set_state(message.chat.id, "add_translate")
        return
    words = json.loads(words)
    amount = len(words)
    if amount == 1:
        word = list(words)[0]
        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text="Добавить в мой словарь", callback_data="add " + word),
                   types.InlineKeyboardButton(text="вернуться в меню", callback_data="menu"),
                   ]
        for bt in buttons:
            keyboard.add(bt)

        words_dict = words
        pos = words_dict[word].get("pos", "")
        level = words_dict[word].get("level", "")
        ts = words_dict[word]["translate"]
        transcription = ts.get("ts", "")
        meanings = ts.get("tr", list())
        examples = ts.get("ex", list())
        synonyms = ts.get("syn", list())
        # Транскрипция: [kɒnstɪˈtjuːʃn]
        # Существительное
        text = f"*{word}*"
        if transcription:
            text += "\nТранскрипция: [" + transcription + "]"
        text += "\n" + pos_dict.get(pos, pos)
        if level and False:
            text += " topic: " + level
        text += "\n"

        for mng in meanings:
            text += "\n· " + mng
            if False and "more":  # обычно ложь, может когда-то заработает
                try:
                    if mng in synonyms and synonyms[mng]:
                        text += "\n  " + "synonyms:\n" + ",".join(synonyms[mng])
                    if mng in examples and examples[mng]:
                        text += "\n  " + "examples:"
                        for exmpl in examples[mng]:
                            text += "\n·" + exmpl["text"]
                            for ex_tr in exmpl["tr"]:
                                text += " - " + ex_tr["text"]

                except Exception as e:
                    print(e)
                    text += "\n error \n"
        if False and "more":
            text += "\n подробная информация. Нужно придумать форматирование. \n"
        data = {"text": text,
                "audio": None,
                "keyboard": keyboard}

        if data["audio"] is None:
            bot_send_message_safe(message.chat.id, data["text"], reply_markup=data["keyboard"],
                                  parse_mode="Markdown")
            return
    bot_send_message_safe(message.chat.id, "```" + str(len(words)) + "```", reply_markup=markups.learn_markup,
                          parse_mode="Markdown")


def dont_understand(message, keyboard=None):
    if not keyboard:
        users.reset_state(message.chat.id)
        keyboard = markups.main_markup
    bot_send_message_safe(message.chat.id,
                          "Прости я тебя не понял, ты можешь общаться со мной через меню.",
                          reply_markup=keyboard)
    photo = open('open_menu.jpg', 'rb')
    bot.send_photo(message.chat.id,
                   photo,
                   reply_markup=keyboard)


def time_notify_message(message):
    if message.text == "Назад в меню":
        users.reset_state(message.chat.id)
        bot_send_message_safe(message.chat.id, "Чем займемся?",
                              reply_markup=markups.main_markup)
    else:
        LangBotApi.send_time_notify(message.chat.id, message.text)


def learn_word_now(id, topic_id=None):
    data = Api().get_new_words(id, topic_id=topic_id)
    if data is False:
        if not is_allowed_or_msg(id):
            return
    placeholder_text = """*📚Начинай учить слова*

В конце будет проверочный тест
👐🏼У тебя все получится

P.S  Я верю в тебя"""
    bot_send_message_safe(id, placeholder_text, reply_markup=markups.end_learn_murkup, parse_mode="Markdown")
    users.set_state(id, "learning_word")
    # Api().get_new_words(id, topic_id=topic_id)
    word_number = 0
    data = LearnWords().get_word_keys_data(id, word_number)
    bot.send_voice(id, data["audio"], data["text"], reply_markup=data["keyboard"],
                   duration=2, parse_mode="Markdown")


def start_game(user_id):
    users.set_state(user_id, "playing_game")
    data = GameApi.get_next_step(user_id)
    bot_send_message_safe(user_id, "Игра началась!", reply_markup=markups.hideBoard, parse_mode="Markdown", )
    bot_send_message_safe(user_id, data["text"], reply_markup=data["keyboard"], parse_mode="Markdown", )


def do_game_results(data):
    winner = data[2]
    if winner is not None:
        looser = list(data[0])
        looser.remove(winner)
        looser = looser[0]
        print(winner)

        if (data[0][winner][1] < data[0][looser][1] or
                (data[0][winner][1] == data[0][looser][1] and
                 (data[0][looser][3] - data[1]) < (data[0][winner][3] - data[1]))):
            winner, looser = looser, winner
        print(winner)
        # winner_score = f"баллов:{data[0][winner][1]}; время:{(data[0][winner][2]-data[1]).seconds} секунд"
        # looser_score = f"баллов:{data[0][looser][1]}; время:{(data[0][looser][2]-data[1]).seconds} секунд"
        # winner_text = "Вы победили! Ваш счет:\n"+winner_score+"\n\n"+looser_score
        # looser_text = "Вы проиграли. Ваш счет:\n"+looser_score+"\n\n"+winner_score
        emojis_win_loose = [("🍀", "🌵"),
                            ("🦁", "🐌"),
                            ("🏆", "🥦"),
                            ("🎖", "🥈"),
                            ("🏅", "🌚"),
                            ]
        emojis_win_loose = random.choice(emojis_win_loose)
        text = f"""1) {emojis_win_loose[0]} {data[0][winner][2]['first_name']} - {data[0][winner][1]} баллов ({(data[0][winner][3] - data[1]).seconds} сек.)
2) {emojis_win_loose[1]} {data[0][looser][2]['first_name']} - {data[0][looser][1]} баллов ({(data[0][looser][3] - data[1]).seconds} сек.)
        
        """
        winner_text = text + """Победа 🎉! (+ ❤)"""
        looser_text = text + """Поражение."""
        # some_text="""
        #
        # 😋 Посмотреть мои достижения (https://inmind.tech/rating/16.04.2020/151205975)"""

        bot_send_message_safe(winner, winner_text, reply_markup=markups.main_markup)
        bot_send_message_safe(looser, looser_text, reply_markup=markups.main_markup)
        LangBotApi.add_rating(winner, 5)


# bot.polling(True)


# def main_loop():
#     bot.polling(none_stop=False, timeout=20)
#     while 1:
#         time.sleep(3)
#
#
# if __name__ == '__main__':
#         try:
#             main_loop()
#         except KeyboardInterrupt:
#             print('\nExiting by user request.\n')
#             sys.exit(0)
#         except Exception as e:
#             for i in dev_ids:
#                 dev_bot.send_message(i, e, reply_markup=markups.main_markup)
#             print(e)
#             raise(e)
#             time.sleep(3)

while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print("Ошибка: ", e)
        import traceback

        try:
            for i in dev_ids:
                dev_bot.send_message(i, e, reply_markup=markups.main_markup)
        except Exception as e:
            print("TESTBOT FAILED")
            print(e)
        traceback.print_exc()  # или просто print(e) если у вас логгера нет,
        # или import traceback; traceback.print_exc() для печати полной инфы
        time.sleep(5)
# def main_loop():
# bot.infinity_polling(none_stop=True, timeout=3)
# while 1:
#     time.sleep(3)


# if __name__ == '__main__':
#     main_loop()
#     while 1:
#         try:
#             bot.stop_bot()
#             print("bot stopped")
#             time.sleep(3)
#             main_loop()
#             print("MAIN LOOP FINISHED\n"*10)
#         except KeyboardInterrupt:
#             print('\nExiting by user request.\n')
#             sys.exit(0)
#         except Exception as e:
#             try:
#                 # bot.worker_pool = util.ThreadPool(num_threads=2)
#                 # bot.stop_bot()
#                 for i in dev_ids:
#
#                     bot.send_message(i, "f __name__ == '__main__':", reply_markup=markups.main_markup)
#                     bot.send_message(i, e, reply_markup=markups.main_markup)
#                 print(e)
#             except Exception as e:
#                 print("LOL EXCEPTION IN EXCEPTION\n"*20) #
#                 print(e)
#             time.sleep(3)
#
#             raise(e)
#         time.sleep(3)
# print("ANOTHER TRY IN MAIN_LOOP\n" * 10)

# print("bot FILE FINISHED\n" * 10)
