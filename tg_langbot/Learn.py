from Api import Api, get_audio, get_tg_link
from telebot import types
import random

from BackendApi import LangBotApi

BASE_URL_IMAGE = "http://0.0.0.0:8000"
pos_dict = {
    "indefinite article": "Неопределнный артикль",
    "verb": "Глагол",
    "noun": "Существиельное",
    "adjective": "Прилагательное",
    "adverb": "Наречие",
    "preposition": "Предлог",
    "pronoun": "pronoun",

}
levels_str = {"начальный": "Beginner",
              "a1": "Elementary",
              "a2": "Pre-Intermediate",
              "b1": "Intermediate",
              "b2": "Upper-Intermediate",
              "c1": "Advanced",
              "c2": "Proficiency"
              }


class LearnWords:

    def start_learning(self, chat_id):
        data = Api().get_new_words(chat_id)
        if data is False:
            if not Api().is_allowed_today(chat_id):
                return
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Я все запомнил️", callback_data="remembered")
        keyboard.add(button)
        text = "\n".join([key + " - " + "data[key]" for key in data])
        return {"keyboard": keyboard, "text": text}

    def get_word_keys_data(self, chat_id, word_number, more=False):
        words_list, words_dict = Api().get_list_words(chat_id)
        n_words = len(words_list)
        word_number = int(word_number)
        prev_n = word_number - 1 if word_number else word_number
        next_n = word_number + 1 if word_number + 1 < n_words else word_number

        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text="⬅️", callback_data="goto " + str(prev_n))]
        buttons += [
            types.InlineKeyboardButton(text=str(word_number + 1) + "/" + str(n_words), callback_data="start_quiz")]
        buttons += [types.InlineKeyboardButton(text="➡️", callback_data="goto " + str(next_n))]
        buttons += [types.InlineKeyboardButton(text="Подробнее", callback_data="more " + str(word_number))]
        buttons += [types.InlineKeyboardButton(text="Перейти к тесту", callback_data="start_quiz")]
        keyboard.add(*buttons[:3])
        keyboard.add(buttons[3])
        if word_number + 1 == n_words:
            keyboard.add(buttons[4])

        word = words_list[word_number]


        pos = words_dict[word].get("pos", "")
        level = words_dict[word].get("level", "")

        ts = words_dict[word]["translate"]
        audio = words_dict[word].get("audio", "")
        audio = LangBotApi.get_word_audio_by_path(audio)
        transcription = ts.get("ts")
        meanings = ts.get("tr")
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
            if more:  # обычно ложь, может когда-то заработает
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
        if more:
            text += ""
        data = {"text": text,
                "audio": audio,
                "keyboard": keyboard}

        return data

    def check_memorized(self, chat_id, correct_answer=None):
        next_word, next_word_translate = Api().get_next_word(chat_id)
        if next_word is None:  # завершение обучения
            LangBotApi.add_rating(chat_id, 5)
            text = "Изучение слов завершенно, получи 5 ❤\n\n"
            text += """🔹Теперь эти слова ты можешь изучать в *Интервальном повторении*, для того чтобы быстрее их запомнить

🔹Ты можешь учить неограниченное количество слов в разделе *Изучать слова*, по 10/20/50 в день! 
"""
            keyboard = types.InlineKeyboardMarkup()
        else:
            randoms_words = Api().get_random_words(chat_id)
            keyboard = types.InlineKeyboardMarkup()
            buttons = [types.InlineKeyboardButton(text=next_word_translate, callback_data="good " + next_word)]
            for word in list(randoms_words):
                buttons.append(types.InlineKeyboardButton(text=word, callback_data="bad"))
            random.shuffle(buttons)
            for bt in buttons:
                keyboard.add(bt)
            text = ""
            if correct_answer is not None:
                text += "**Неверно!**\nПравильный ответ:\n"
                text += correct_answer[0] + " - " + correct_answer[1] + "**\n\n"
                text += "возможно нужна кнопка подробной информации"
            text += "*Выбери правильный перевод*\n\n"
            text += f"*{next_word}*"

        return {"keyboard": keyboard, "text": text}

    def good_answer(self, chat_id):
        Api().poor_learned_one_word(chat_id)
        Api().remove_good_word(chat_id)
        return self.check_memorized(chat_id)

    def next_answer(self, chat_id):
        return self.check_memorized(chat_id)

    def bad_answer(self, chat_id):
        words_list, words_dict = Api().get_list_words(chat_id)
        data = self.get_word_keys_data(chat_id, words_list.index(Api().get_good_word(chat_id)[0]))
        data['text'] = "Неправильно!\n" + data["text"]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Запомнил(а)", callback_data="next"))
        data["keyboard"] = keyboard
        # print("1\n"*5, Api().get_good_word(chat_id),"2\n"*5, sep = "\n"*5)
        return data
        # return self.check_memorized(chat_id, correct_answer = Api().get_good_word(chat_id))


class TestLevel:

    def test_question_data(self, chat_id):
        next_word, next_word_translate, count = Api().get_next_test_word(chat_id)
        if next_word is None:  # завершение обучения
            goal = 80
            score = Api().get_test_score(chat_id)
            percent = int((score[0] / score[1]) * 100)
            if percent > goal:
                LangBotApi.add_rating(chat_id, 20)
                text = "Поздравляю! Тест завершен.\nВы получили новый уровень: *" + \
                       levels_str[Api().get_next_level(chat_id)] + "* и 20 ❤"
                Api().set_next_level(chat_id)
            else:
                text = "Тест завершен.\n"
                text += "К сожалению, вы не прошли тест.\nДо уровня " + levels_str[Api().get_next_level(chat_id)] + "\n"
                text += "Вам не хватило " + str(goal - percent + 1) + "%"
            text += "\nВы набрали " + str(percent) + "% (" + str(score[0]) + " из " + str(score[1]) + ")."
            keyboard = types.InlineKeyboardMarkup()
        else:
            # randoms_words = Api().get_random_test_words(chat_id)
            randoms_words = Api().get_random_words(chat_id)
            keyboard = types.InlineKeyboardMarkup()
            buttons = [types.InlineKeyboardButton(text=next_word_translate, callback_data="good " + next_word)]
            for word in list(randoms_words):
                buttons.append(types.InlineKeyboardButton(text=word, callback_data="bad"))
            random.shuffle(buttons)
            for bt in buttons:
                keyboard.add(bt)
            text = ""
            text += f"_Осталось {count} вопросов_\n\n"
            text += "**Выбери правильный перевод**\n\n"
            text += f"*{next_word}*"

        return {"keyboard": keyboard, "text": text}

    def test_answer(self, chat_id, good=False):
        Api().remove_test_word(chat_id, good=good)
        return self.test_question_data(chat_id)


class Topics:

    def get_topics(self, user_id=None):
        data = LangBotApi.get_topics()
        topics_b = []
        for topic in data[:50]:
            print(topic)
            if user_id is None:
                text = 'Выбрана тема: ' + topic['name']
                keyboard=None
            else:
                text = 'Вас пригласили на битву!\nТема: ' + topic['name']
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text="принять участвие в игре",
                                                      url=get_tg_link('g'+str(user_id))))
            if topic['image'] and ("http://5.187.6.15" in topic['image']):
                topic['image'] = topic['image'].replace("http://5.187.6.15", "https://botenglish.ru")
            topics_b.append(types.InlineQueryResultArticle(topic['id'],
                                                           title=topic['name'],
                                                           # description='Вами выучено 0 из 54',
                                                           thumb_url=topic['image'],
                                                           input_message_content=types.InputTextMessageContent(
                                                               text),
                                                           reply_markup=keyboard))
        return topics_b
