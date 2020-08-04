import os
import pickle

import requests
from googletrans import Translator


class GooTrans:
    """this class and this bot was written in short time in may 2020
    please do not judge us, we suffered already"""

    def __init__(self):
        self.translator = Translator()

    def trans(self, text, dest='ru'):
        if dest == 'ru':
            try:
                a = self.translator.translate(text, dest=dest)

                w = a.text
                a = a.extra_data["all-translations"][0][1][:5]
                if a[0] != w:
                    a = [w, ] + [i for i in a if i != w]
                return {'tr': a}
            except Exception as e:
                print("failed to translate in trans")
                if "'NoneType' object is not subscriptable" == str(e):
                    return {'tr': ""}
                elif "Expecting value: line 1 column 1 (char 0)" == str(e):
                    os.system("windscribe disconnect")
                    os.system("windscribe connect")
                print(e)
        elif dest == 'en':
            try:
                a = self.translator.translate(text, dest=dest)
                text = a.text
                a = self.translator.translate(text, dest='ru')
                w = a.text
                a = a.extra_data["all-translations"][0][1][:5]
                if a[0] != w:
                    a = [w, ] + [i for i in a if i != w]
                return text, {'tr': a}
            except Exception as e:
                print("failed to translate ru to en in trans")
                print(e)


# count = 0
# for word in list(all_words):
#     if all_words[word].get("translation", "chlen") == "chlen":
#         trans = GooTrans().trans(word, dest="ru")
#         if trans:
#             all_words[word]["translation"] = trans
#             print(word, trans)
#             print(all_words[word])
#         else:
#             print("Не смог перевести", word)
#     if count % 10 == 0:
#         print(count)
#     if count % 50 == 0:
#         print("СОХРАНИЛ", count)
#         with open('all_words_not_db_new.json', 'wb') as json_file:
#             pickle.dump(all_words, json_file, protocol=pickle.HIGHEST_PROTOCOL)
#     count += 1
# print(len(all_words))

def get_audio(link):
    audio = False
    while not audio:
        try:
            res = requests.get(link, timeout=7)
            if res.status_code != 200:
                raise Exception("")
            else:
                audio = res.content
        except Exception as e:
            print(e)
    return audio


with open('parsing/all_words_not_db_new2.json', 'rb') as handle:
    all_words = pickle.load(handle)

count = 0
for word in list(all_words):
    if not all_words[word].get("audio_bin"):
        print("https://www.oxfordlearnersdictionaries.com" + all_words[word].get("audio"))
        audio = get_audio("https://www.oxfordlearnersdictionaries.com" + all_words[word].get("audio"))
        if audio:
            all_words[word]["audio_bin"] = audio
        print(word)
    if count % 10 == 0:
        print(count)
    if count % 50 == 0:
        print("СОХРАНИЛ", count)
        with open('parsing/all_words_not_db_new2.json', 'wb') as json_file:
            pickle.dump(all_words, json_file, protocol=pickle.HIGHEST_PROTOCOL)
    count += 1
