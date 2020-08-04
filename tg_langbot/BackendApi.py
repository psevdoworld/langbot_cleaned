from datetime import datetime

from requests import get, post, patch
import os
BASE_URL = os.environ.get('BASE_URL') or "http://0.0.0.0:8000"
headers = {"BotAuthToken": "example_token"}


class LangBotApi:


    @staticmethod
    def get_user_referals_count(user_id):
        res = get(f"{BASE_URL}/bot_users/referal_count/{user_id}/", headers=headers)
        if res.status_code == 200:
            data = res.json()
            return data
        return False


    @staticmethod
    def get_allowed_date(user_id):
        res = get(f"{BASE_URL}/bot_users/user/{user_id}/", headers=headers)
        if res.status_code == 200:
            print(res.json()["allowed_date"])
            date = res.json()["allowed_date"].split("T")[0]
            return datetime.strptime(date, "%Y-%m-%d")
        return False

    @staticmethod
    def get_users_by_time_notify(time):
        res = get(f"{BASE_URL}/bot_users/user/?notify_time={time}", headers=headers)
        if res.status_code == 200:
            return res.json()
        return False

    @staticmethod
    def get_user(user_id):
        res = get(f"{BASE_URL}/bot_users/user/{user_id}/", headers=headers)
        if res.status_code == 200:
            return res.json()
        return False

    @staticmethod
    def get_user_level(user_id):
        res = get(f"{BASE_URL}/bot_users/user/{user_id}/", headers=headers)
        if res.status_code == 200:
            return res.json()["level"]
        return False

    @staticmethod
    def set_user_level(user_id, level):
        res = patch(f"{BASE_URL}/bot_users/user/{user_id}/",  {"level": level},  headers=headers)
        if res.status_code == 200:
            return res.json()
        return False

    @staticmethod
    def register_user(user, ref_id):
        res = post(f"{BASE_URL}/bot_users/user/",
                   {
                       "tg_id": user.id,
                       "first_name": user.first_name,
                       "username": user.username,
                       "ref_id": ref_id,
                   }, headers=headers
                   )
        if res.status_code == 201:
            return res.json()
        return False

    @staticmethod
    def add_email_user(user_id, email):
        res = patch(f"{BASE_URL}/bot_users/user/{user_id}/",  {"email": email}, headers=headers)
        if res.status_code == 200:
            return True
        return False

    @staticmethod
    def add_translate_word(word, trans):
        res = post(f"{BASE_URL}/dictionary/add_translate_word/",  {"en": word, "ru": trans}, headers=headers)
        if res.status_code == 200:
            return res.content
        return False

    @staticmethod
    def get_words_for_learn(user_id, topic_id):
        if topic_id is None:
            res = get(f"{BASE_URL}/bot_users/user_words_for_learning/{user_id}/", headers=headers)
        else:
            res = get(f"{BASE_URL}/bot_users/words_from_topic_for_user?tg_id={user_id}&topic={topic_id}", headers=headers)

        if res.status_code == 200:
            return res.json()
        return False

    @staticmethod
    def get_words_for_game(topic_id):
        res = get(f"{BASE_URL}/bot_users/words_from_topic_for_game?topic={topic_id}", headers=headers)

        if res.status_code == 200:
            return res.json()
        return False

    @staticmethod
    def get_words_for_test(user_id):
        res = get(f"{BASE_URL}/bot_users/user_words_for_test/{user_id}/", headers=headers)
        # res = get(f"{BASE_URL}/bot_users/user_words_for_learning/{user_id}", headers=headers)

        if res.status_code == 200:
            return res.json()
        return False

    @staticmethod
    def get_word_audio(word):
        res = get(f"{BASE_URL}/media/audio/mp3/{word}.mp3", headers=headers)
        if res.status_code == 200:
            return res.content
        return False

    @staticmethod
    def get_word_audio_by_path(audio):
        print(audio)
        #audio = "media/audio/media/audio/gTTS_audio_mp3/iphone_zBCKdal.mp3"
        res = get(f"{BASE_URL}/media/{audio}", headers=headers)
        print(res.status_code)
        print(f"{BASE_URL}/{audio}")
        if res.status_code == 200:
            return res.content
        return False


    @staticmethod
    def get_word_translate(word):
        res = get(f"{BASE_URL}/dictionary/translate_by_word/{word}/", headers=headers)
        if res.status_code == 200:
            return res.content
        return False

    @staticmethod
    def add_world_user(user_id, word):
        print(user_id, word)
        res = post(f"{BASE_URL}/dictionary/add_word_to_user/", {"tg_id": user_id, "word": word}, headers=headers)
        if res.status_code == 200:
            return True
        return False

    @staticmethod
    def change_word_status(user_id, word):
        res = post(f"{BASE_URL}/bot_users/change_word_status/", {"tg_id": user_id, "word": word}, headers=headers)
        if res.status_code == 200:
            return True
        return False

    @staticmethod
    def get_user_dict(user_id, page):
        res = get(f"{BASE_URL}/bot_users/get_user_dict/{user_id}/?page={page}", headers=headers)
        if res.status_code == 200:
            return res.json()
        return False

    @staticmethod
    def send_time_notify(user_id, time):
        res = patch(f"{BASE_URL}/bot_users/user/{user_id}/", {"notify_time": "" if time is None else time}, headers=headers)
        if res.status_code == 200:
            return True
        return False


    @staticmethod
    def get_word_to_repeat(user_id):
        res = get(f"{BASE_URL}/bot_users/get_word_to_repeat/{user_id}/", headers=headers)
        if res.status_code == 200:
            return res.json()
        return False

    @staticmethod
    def change_repeat_word_status(user_id, prev_word_id, mem_status):
        res = post(f"{BASE_URL}/bot_users/change_repeat_word_status/",
                   {"tg_id": user_id, "word_id": prev_word_id, "mem_status": mem_status},
                   headers=headers)
        if res.status_code == 200:
            return True
        return False

    @staticmethod
    def get_topics():
        res = get(f"{BASE_URL}/dictionary/topics/", headers=headers)
        if res.status_code == 200:
            return res.json()
        return False

    # Логи статистики
    @staticmethod
    def message_log(message):
        res = post(f"{BASE_URL}/stats/message_log/", {"message": message}, headers=headers)

    @staticmethod
    def call_log(call):
        res = post(f"{BASE_URL}/stats/call_log/", {"call": call}, headers=headers)

    @staticmethod
    def support_message(message):
        data = {
            "chat_id": message.chat.id,
            "user_name": message.from_user.username,
            "message_id": message.message_id,
            "text": message.text,
            "message": message
        }
        res = post(f"{BASE_URL}/stats/support_message/", data, headers=headers)

    @staticmethod
    def get_progress(chat_id):
        res = get(f"{BASE_URL}/bot_users/{chat_id}/stats/", headers=headers)
        if res.status_code == 200:
            return res.json()
        return False

    @staticmethod
    def add_rating(tg_id, count):
        res = post(f"{BASE_URL}/bot_users/add_rating/", {"tg_id": tg_id, "count": count}, headers=headers)

    @staticmethod
    def general_rating():
        res = get(f"{BASE_URL}/bot_users/general_rating/", headers=headers)
        if res.status_code == 200:
            return res.json()

    @staticmethod
    def general_daily_rating():
        res = get(f"{BASE_URL}/bot_users/general_daily_rating/", headers=headers)
        if res.status_code == 200:
            return res.json()

    @staticmethod
    def get_pay_link(tg_id, amount):
        res = post(f"{BASE_URL}/payments/get_pay_link/", {"tg_id": tg_id, "amount": amount}, headers=headers)
        if res.status_code == 200:
            return res.json()
