from telebot import types
from Api import get_tg_link
hideBoard = types.ReplyKeyboardRemove()

main_markup = types.ReplyKeyboardMarkup()
main_markup.add('📚Учиться', '🤳Игры',)
main_markup.add('🗽Болталка', '📈Мой Прогресс')
main_markup.add('⏱Расписание', '👥Общий рейтинг')
main_markup.add('👐🏼Пригласить', '📱Личный кабинет')

learn_markup = types.ReplyKeyboardMarkup()
learn_markup.add('🔄Изучать слова', '🔎Перевести слово')
learn_markup.add('⏰Интервальное повторение')
learn_markup.add("🆗Проверить уровень", '📝Мой словарь')
learn_markup.add('🤳Меню', '⏱Расписание')


cabinet_markup = types.ReplyKeyboardMarkup()
cabinet_markup.add('💰Оплата')
cabinet_markup.add('🆘Поддержка')
cabinet_markup.add('🤳Меню')

referal_markup = types.ReplyKeyboardMarkup()
referal_markup.add('отправить ссылку в телеграме')
referal_markup.add('создать универсальную ссылку')
referal_markup.add('Назад в меню')

pay_markup = types.ReplyKeyboardMarkup()
pay_markup.add('Месяц - 159 руб ')
pay_markup.add('3 месяца - 299 руб')
pay_markup.add('Год - 990 руб')
pay_markup.add('Назад в меню')


def get_referal_markup(chat_id):
    referal_markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text="отправить ссылку в телеграме",
                                          url=f"https://telegram.me/share/url?url={get_tg_link(chat_id)}&text= ")]
    buttons += [types.InlineKeyboardButton(text="сгенерировать ссылку для других сайтов", callback_data="share_link")]
    for bt in buttons:
        referal_markup.add(bt)
    return referal_markup

# def get_game_start_keyboard(chat_id):
#     referal_markup = types.InlineKeyboardMarkup()
#     referal_markup.add(types.InlineKeyboardButton(text="принять участвие в игре",
#                                           url=get_tg_link('g'+str(chat_id))))
#     return referal_markup
#
#
# def get_game_invite_keyboard(chat_id):
#     keyboard = types.InlineKeyboardMarkup()
#     keyboard.add(types.InlineKeyboardButton(text="выбрать оппонента", switch_inline_query="send_game_invite"))
#
#     # referal_markup = types.InlineKeyboardMarkup()
#     # referal_markup.add(types.InlineKeyboardButton(text="принять участвие в игре",
#     #                                       url=get_tg_link('g'+str(chat_id))))
#     return keyboard


end_learn_murkup = types.ReplyKeyboardMarkup()
end_learn_murkup.add('Закончить обучение')
end_learn_murkup.add('Назад в меню')

end_test_murkup = types.ReplyKeyboardMarkup()
end_test_murkup.add('Прервать тест')
end_test_murkup.add('Назад в меню')

time_notify_markup = types.ReplyKeyboardMarkup()

time_notify_markup.add('9:00', '12:00', '13:00')
time_notify_markup.add('14:00', '18:00', '19:00')
time_notify_markup.add('20:00', '21:00', '22:00')
time_notify_markup.add('Отключить уведомления','Назад в меню')

stop_talk_murkup = types.ReplyKeyboardMarkup()
stop_talk_murkup.add('Я устал болтать')

add_word_tr_markup = types.InlineKeyboardMarkup()
add_word_tr_markup.add(types.InlineKeyboardButton(text="Вернуться к обучению", callback_data="fuck_go_back"))



button_list = ['📚Учиться', '🤳Игры', '🗽Болталка', '📈Мой Прогресс', '⏱Расписание', '👥Общий рейтинг',
                '👐🏼Пригласить', '📱Личный кабинет', '🔄Изучать слова', '🔎Перевести слово',
                '⏰Интервальное повторение', "🆗Проверить уровень", '📝Мой словарь', '🤳Меню', '⏱Расписание',
                '💰Оплата', '🆘Поддержка', '🤳Меню', 'Назад в меню', 'Закончить обучение']
