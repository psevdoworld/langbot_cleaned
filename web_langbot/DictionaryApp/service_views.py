import json
import os
from django.http import JsonResponse
from rest_framework import status
from django.core.files import File
from translate import Translator

# from parsing.pars_oxford import pars_words
from DictionaryApp.models import Translation


def create_oxford_topic(request):
    url = request.GET["url"]
    oxford_dict = {}  # не работчая view
    write_to_file(oxford_dict)
    for word in list(oxford_dict)[:0]:
        print("#"*40)
        print(word, oxford_dict[word])
        # word_trans = YaDict().trans(word, oxford_dict[word]["pos"])
        translator = Translator(to_lang="ru")
        try:
            word_trans = translator.translate(word)
            if word_trans != word:
                print(word, word_trans)
                oxford_dict[word]["translation"] = word_trans
            else:
                raise Exception("Нет перевода!")
        except Exception as e:
            print(word, e)
            del oxford_dict[word]
        import time
        time.sleep(0.5)
    import pprint
    pprint.pprint(oxford_dict)
    return JsonResponse({}, status=status.HTTP_200_OK)

def generate_oxford_5000(request):
    f = open("data_old.json", "r")
    data = json.loads(f.read())
    # pprint.pprint(data)
    for word in list(data)[:]:
        try:
            word_obj = Translation(lang_key="eng_rus",
                                   word=word,
                                   pos=data[word]["pos"],
                                   oxford_level=data[word]["level"])
            word_obj.translation = data[word]["translate"] or {}
            f = open("media/oxford_mp3/"+word+".mp3", "rb")
            file = File(f)
            file.name = "mp3/" + word + ".mp3"
            word_obj.audio = file
            check_file("media/audio/" + word + ".mp3")
            word_obj.save()
        except Exception as e:
            print(e)
        print(word)
    return JsonResponse({}, status=status.HTTP_200_OK)


def check_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)


def write_to_file(words_dict):
    with open('data_topic.json', 'w', encoding='utf8') as json_file:
        json.dump(words_dict, json_file, ensure_ascii=False)
