from BackendApi import LangBotApi
from telebot import types
from markups import main_markup, learn_markup
from Learn import pos_dict

class Users:

    def __init__(self):
        self.users_stat = {}
        self.api = LangBotApi

    def get_state(self, user, ref_id=None):
        # на тот случай, если юзера удалили из бд
        # check_user = self.api.get_user(user.id)
        # if not check_user:
        #     self.users_stat.pop(user.id, None)

        state = self.users_stat.get(user.id)
        if not state:
            check_user = self.api.get_user(user.id)
            if not check_user:
                new_user = self.api.register_user(user, ref_id)
                if new_user:
                    self.set_state(user.id, "email")
                    return "email"
                    self.reset_state(user.id)
                    state = self.users_stat.get(user.id)
            self.reset_state(user.id)
            state = self.users_stat.get(user.id)
        return state

    def set_state(self, chat_id, state):
        self.users_stat[chat_id] = state

    def reset_state(self, chat_id):
        self.users_stat[chat_id] = "init"

    def get_progress(self, chat_id):
        print("users count ",len(self.users_stat))
        data = LangBotApi.get_progress(chat_id)
        print(data)
        text = "\n*Рейтинг:* " + str(data["rating"]) + " ❤"
        text += "\n*Словарный запас:* " + str(data["count_words"])
        text += "\n*Сегодня изучено:* " + str(data["count_words_today"])
        text += "\n*Новых слов за неделю:* " + str(data["count_words_week"])
        text += "\n*Непрерывная серия:* " + str(data["lifelong_learning"])
        return text

    def edit_notify(self, user, time):
        print("Уведолмения установлены")
        LangBotApi.send_time_notify(user, time)

class UsersDict:

    def get_user_dict(self,  user_id, page=1):
        data = LangBotApi.get_user_dict(user_id, page=page)
        text = ""
        for item in data["words"]:
            word = f"*{item}*"
            tr = data["words"][item]["translate"].get("tr", ["нет перевода"])[0]
            text += f"\n{word} - {tr}"
        return text, self.pages_keyboard(page, data["pages"])

    def pages_keyboard(self, curr_page, all_page):
        prev_page = curr_page - 1 if curr_page > 1 else 1
        next_page = curr_page + 1 if curr_page != all_page else all_page
        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text="⬅️", callback_data="goto " + str(prev_page))]
        buttons += [types.InlineKeyboardButton(text=str(curr_page) + "/" + str(all_page), callback_data="help")]
        buttons += [types.InlineKeyboardButton(text="➡️", callback_data="goto " + str(next_page))]
        keyboard.add(*buttons)
        return keyboard


class UsersRepeat:

    def __init__(self):
        self.users_word_to_repeat = {}
        self.users_rating = {}

    def open_card(self, user_id):
        user_word = self.users_word_to_repeat.get(user_id)
        if user_word:
            text = self.gen_translate_text(user_word)
            keyboard = self.memorable_keyboard()
            return text, keyboard
        return None, None

    def next_word(self, user_id, mem_status):
        if mem_status in ("good" or "not_good"):
            self.users_rating[user_id] = self.users_rating.get(user_id, 0) + 1
        prev_word_id = self.users_word_to_repeat.get(user_id, dict()).get("id")
        LangBotApi.change_repeat_word_status(user_id, prev_word_id, mem_status)
        return self.get_word_to_repeat(user_id)

    def get_word_to_repeat(self, user_id):
        word = LangBotApi.get_word_to_repeat(user_id)
        if isinstance(word, dict):
            self.users_word_to_repeat[user_id] = word
            text = '_(↘️ Нажми Показать перевод, чтобы проверить себя)_'
            text += "\n\nПомнишь слово *" + word.get('word') + "* ?"
            keyboard = self.open_card_keyboard()
            return text, keyboard
        else:
            rating = self.users_rating.get(user_id)
            if rating:
                LangBotApi.add_rating(user_id, rating)
                self.users_rating.pop(user_id, None)
                return f"Сегодня больше нет слов для повторения получи {rating} ❤", learn_markup
            else:
                return "Сегодня больше нет слов для повторения.", learn_markup

    @staticmethod
    def open_card_keyboard():
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Показать перевод", callback_data="open_card")
        keyboard.add(button)
        return keyboard

    @staticmethod
    def memorable_keyboard():
        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(text="Не помню", callback_data="bad")]
        buttons += [types.InlineKeyboardButton(text="Плохо помню", callback_data="not_good")]
        buttons += [types.InlineKeyboardButton(text="Помню", callback_data="good")]
        keyboard.add(*buttons)
        return keyboard

    @staticmethod
    def gen_translate_text(word):

        ts = word["translation"]
        transcription = ts.get("ts")
        pos = word.get("pos", "pos")
        meanings = ts.get("tr")
        word = word["word"]
        text = f"*{word}*"
        if transcription:
            text += "\nТранскрипция: [" + transcription + "]"
        text += "\n" + pos_dict.get(pos, pos)
        text += "\n"
        for mng in meanings:
            text += "\n· " + mng
        return text

