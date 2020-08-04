import random
from datetime import datetime

from telebot import types

import markups
from BackendApi import LangBotApi

invites = dict()
game_data = dict()
class GameApi:
    @staticmethod
    def new_game_invite(user_id, topic_id):
        global invites
        print("invites", len(invites))

        invites[user_id] = topic_id


    @staticmethod
    def accept_invite(ref_id, user_id):
        global invites

        if ref_id in invites:
            topic = invites[ref_id]
            return topic

    @staticmethod
    def start_game(ref_id, user_id):
        global game_data, invites

        if ref_id in invites:
            topic = invites[ref_id]
            del invites[ref_id]
            data = LangBotApi.get_words_for_game(topic)
            words = list(data)
            random.shuffle(words)

            ref_user = LangBotApi.get_user(ref_id)
            user_user = LangBotApi.get_user(user_id)
            try:
                if not (ref_user and user_user):
                    print("WTF\n"*10)
                    print(ref_user, user_user)
                    print(topic)
                    print(ref_id, user_id)
            except Exception as e:
                print(e)
            game_data[ref_id] = [words,
                                 data,
                                 {ref_id: [-1, 0, ref_user], user_id:[-1, 0, user_user]},
                                 datetime.now(),
                                 None]

            game_data[user_id] = game_data[ref_id]
            return topic

    @staticmethod
    def get_next_step(user_id, good = False):
        global game_data
        if good:
            game_data[user_id][2][user_id][1] += 1
        game_data[user_id][2][user_id][0]+=1
        word_n = game_data[user_id][2][user_id][0]
        if word_n < len(game_data[user_id][0]):
            next_word = game_data[user_id][0][word_n]

            next_word_translate = game_data[user_id][1][next_word]["translate"]["tr"][0]
            words = game_data[user_id][0]
            random_words=random.sample(words[:word_n]+words[word_n+1:], 2)
            random_words = [game_data[user_id][1][rw]["translate"]["tr"][0] for rw in random_words]
            keyboard = types.InlineKeyboardMarkup()
            buttons = [types.InlineKeyboardButton(text=next_word_translate, callback_data="good_game")]
            for word in random_words:
                buttons.append(types.InlineKeyboardButton(text=word, callback_data="bad_game"))
            random.shuffle(buttons)
            for bt in buttons:
                keyboard.add(bt)
            you = game_data[user_id][2][user_id]
            him = list(game_data[user_id][2])
            him.remove(user_id)
            his_id = him[0]
            him=game_data[user_id][2][his_id]

            if you[1] > him[1]:
                game_data[user_id][4] = user_id
            text = f"{you[2]['first_name']}:\n{you[0]+1} из {len(words)} (баллы:{you[1]} )\n"
            print(him)
            if him[0] == len(words):
                text += f"{him[2].get('first_name','противник')}:\nзавершено (баллы:{him[1]} )\n"
            else:
                text += f"{him[2].get('first_name','противник')}:\n{him[0]+1} из {len(words)} (баллы:{him[1]} )\n"
            text += "\n**Выбери правильный перевод**\n\n"
            text += next_word
            results = None
            opponent = him[2]['first_name']
        else:
            results = GameApi.exit_game(user_id)
            text = "Вы ответили на все вопросы!\n Ждем вашего оппонента для подведения итогов."
            keyboard = markups.main_markup
            opponent = None

        return {"text": text, "keyboard": keyboard, "results": results, "opponent": opponent}

    @staticmethod
    def exit_game(user_id):
        global game_data
        game_data[user_id][2][user_id].append(datetime.now())
        him = list(game_data[user_id][2])
        him.remove(user_id)
        his_id = him[0]
        if his_id not in game_data:
            data = game_data[user_id]
            return data[2:]
        del game_data[user_id]

    @staticmethod
    def exit_games_if_its_time():
        global game_data
        # print(43)
        # print(game_data)
        results = list()
        for i in list(game_data):
            print(i,datetime.now() - game_data[i][3])
            if (datetime.now() - game_data[i][3]).seconds<300:
                res = GameApi.exit_game(i)
                if res is not None:
                    results.append(res)
        if results:
            return results
