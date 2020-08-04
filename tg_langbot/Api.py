import random
import json
from datetime import datetime

from BackendApi import LangBotApi
# def get_all_word():
#     f = open("data.json", "r")
#     words_dict = json.loads(f.read())
#     return words_dict
# #
def get_audio(word):
    f = open("../web_langbot/media/oxford/" + word + ".ogg", "rb")
    return f.read()


# users_words_dict = {
#     "campfire": "костер", "axe": "топор", "torch": "факел", "seads": "семена",
#     "pure":"без примесей","clean":"чистый","distiled":"дистилированный",
#     "mine":"мой, шахта","you":"ты",
#     "trip":"поездка","answer":"ответ","good":"хорошо","hell":"ад",
# }
bot_name = ""
users_words_dict = dict()
for_memorized = dict()
for_test = dict()
test_score = dict()
current_word = dict()
good_word = dict()
poor_learned_words_count = dict()
next_levels = {"начальный": "a1",
              "a1": "a2",
              "a2": "b1",
              "b1": "b2",
              "b2": "c1",
                "c1": "c1"
              }
end_dates = dict()


def set_bot_name(name):
    global bot_name
    bot_name = name


def get_tg_link(chat_id):
    return f"https://t.me/{bot_name}?start={chat_id}"


def get_public_link(chat_id):
    return f"https://tggo.top/{bot_name}?start={chat_id}"

def detect(word):
    import string
    if word[0].lower() in string.ascii_lowercase:
        return "en"
    else:
        return "ru"

class Api:
    def poor_learned_one_word(self, chat_id):
        global poor_learned_words_count
        if not self.is_allowed_today(chat_id):
            poor_learned_words_count[chat_id] += 1
        else:
            poor_learned_words_count[chat_id] = 0
        print(poor_learned_words_count[chat_id])


    def get_current_level(self, chat_id):
        level = LangBotApi.get_user_level(chat_id)
        if bool(level) is False:
            level = "начальный"
        return level

    def get_next_level(self, chat_id):
        if self.get_current_level(chat_id) in next_levels:
            return next_levels[self.get_current_level(chat_id)]

    def set_next_level(self, chat_id):
        if self.get_next_level(chat_id) is not None:
            LangBotApi.set_user_level(chat_id, self.get_next_level(chat_id))

    def is_allowed_today(self, chat_id):
        global end_dates
        present_day = datetime.now()
        if True or chat_id not in end_dates or end_dates[chat_id] < present_day:
            end_dates[chat_id] = LangBotApi.get_allowed_date(chat_id)
        if type(end_dates[chat_id]) is bool:
            print(chat_id,"is_allowed_today(self, chat_id): is bool")
            return True
        end_day = end_dates[chat_id]
        return end_day.date() >= present_day.date()

    def get_allowed_days_date(self, chat_id):
        global end_date
        present_day = datetime.now()
        end_dates[chat_id] = LangBotApi.get_allowed_date(chat_id)
        end_day = end_dates[chat_id]
        return (end_day - present_day).days + 1, end_day

    def get_list_words(self, chat_id):
        global for_memorized
        words_list = list(for_memorized[chat_id])
        words_list.sort()
        return words_list, {word: users_words_dict[word] for word in words_list}

    def get_new_words(self, chat_id, topic_id=None):
        global for_memorized
        global users_words_dict
        global poor_learned_words_count
        if self.is_allowed_today(chat_id):
            data = LangBotApi.get_words_for_learn(chat_id, topic_id)
            poor_learned_words_count[chat_id] = 0
        else:
            if chat_id not in poor_learned_words_count:
                poor_learned_words_count[chat_id] = 0
            if poor_learned_words_count[chat_id] >= 5:
                return False
            n_words = poor_learned_words_count[chat_id]
            print(n_words)

            data = LangBotApi.get_words_for_learn(chat_id, topic_id)
            data = {i: data[i] for i in list(data.keys())[:5-n_words]}
        users_words_dict.update(data)
        for_memorized[chat_id] = list(data)
        return data

    def start_new_test(self, chat_id):
        global users_words_dict, for_test, test_score, current_word

        data = LangBotApi.get_words_for_test(chat_id)
        if data:
            users_words_dict.update(data)
            for_test[chat_id] = list(data)
            test_score[chat_id] = [0, len(data)]
            current_word[chat_id] = None
            return data

    def get_test_score(self, chat_id):
        return test_score[chat_id]



    def remove_good_word(self, chat_id):
        global current_word
        global for_memorized
        if chat_id in current_word:
            if current_word[chat_id] in for_memorized[chat_id]:
                word_index = for_memorized[chat_id].index(current_word[chat_id])
                del for_memorized[chat_id][word_index]
            word = current_word[chat_id]
            current_word[chat_id] = None
            return word

    def remove_test_word(self, chat_id, good=False):
        global current_word, for_test, test_score
        if chat_id in current_word:
            if current_word[chat_id] in for_test[chat_id]:
                word_index = for_test[chat_id].index(current_word[chat_id])
                del for_test[chat_id][word_index]
            word = current_word[chat_id]
            current_word[chat_id] = None
            if good:
                test_score[chat_id][0] += 1
            return word

    def get_good_word(self, chat_id):
        return current_word[chat_id], good_word[chat_id]

    def get_next_test_word(self, chat_id):
        global for_test, current_word, good_word, poor_learned_words_count
        if chat_id not in poor_learned_words_count:
            poor_learned_words_count[chat_id] = 0

        poor_learned_words_count[chat_id] += 1
        if not for_test[chat_id]:
            return None, None, len(for_test[chat_id])
        word = random.choice(for_test[chat_id])
        current_word[chat_id] = word
        tr_word = random.choice(users_words_dict[word]["translate"]["tr"][:1])
        # good_word[chat_id] = tr_word
        return word, tr_word, len(for_test[chat_id])

    def get_next_word(self, chat_id):
        global for_memorized, current_word, good_word
        if not for_memorized[chat_id]:
            return None, None
        word = random.choice(for_memorized[chat_id])
        current_word[chat_id] = word
        tr_word = random.choice(users_words_dict[word]["translate"]["tr"][:1])
        good_word[chat_id] = tr_word
        return word, tr_word

    @classmethod
    def get_random_words(cls, chat_id):
        dict_values_list = list(users_words_dict.values())
        dict_values_list.remove(users_words_dict[current_word[chat_id]])
        words = []
        while len(words) < 2:
            word = random.choice(dict_values_list)
            if word.get("translate") is not None and word.get("translate").get("tr") is not None and word not in words:
                words.append(word)
        return (random.choice(word["translate"]["tr"]) for word in words)

