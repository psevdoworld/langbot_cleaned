import json

from django.core.files import File
from django.shortcuts import render
# Create your views here.
# api/views.py
from gtts import gTTS
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from DictionaryApp.models import Topics, Translation, UsersWord
from DictionaryApp.serialisers import TopicsSerializer, TranslationSerializer
from DictionaryApp.utils import YaDict, GooTrans
from bot_users.models import BotUser
from web_langbot.permission import OnlyBot

from bot_users.app_user import AppUser


class TopicsViewSet(viewsets.ModelViewSet):
    queryset = Topics.objects.filter(available=True)
    serializer_class = TopicsSerializer


class TranslationViewSet(viewsets.ModelViewSet):
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    lookup_url_kwarg = "word"
    # def get_queryset(self):
    #     self.get_object()
    #     return Translation.objects.all()

def add_audio(word_obj):
    try:
        x = word_obj
        if str(x.audio) == "":
            speech = gTTS(text=x.word, lang="en", slow=False)
            paht = f"media/audio/gTTS_audio_mp3/{x.word}.mp3"
            speech.save(f"media/audio/gTTS_audio_mp3/{x.word}.mp3")
            f = open(paht, 'rb')
            file = File(f)
            file.name = "gTTS/" + x.word + ".mp3"
            x.audio = file
            x.save()
            f.close()
            file.close()
    except Exception as e:
        print("gtts for new word failed, id :", word_obj.id, e)





def detect(word):
    import string
    if word[0].lower() in string.ascii_lowercase:
        return "en"
    else:
        return "ru"

@api_view(['GET'])
@permission_classes([OnlyBot])
def translate_by_word(request, word):
    word = word.lower()
    if detect(word) == 'en':
        word_obj = Translation.objects.filter(word=word).first()
        if word_obj and len(word_obj.translation) == 0:
            return Response({"Слово не найдено"}, status=status.HTTP_404_NOT_FOUND)
        elif not word_obj:
            trans = YaDict().trans(word) or GooTrans().trans(word)
            if trans:
                word_obj, created = Translation.objects.update_or_create(word=word, translation=trans, lang_key="eng_rus")
                if created:
                    add_audio(word_obj)

            else:
                return Response({"Слово не найдено"}, status=status.HTTP_404_NOT_FOUND)
        words_dict_for_bot = {word_obj.word: {"translate": word_obj.translation}}
        return Response(words_dict_for_bot)
    elif detect(word) == 'ru':
        words_obj = Translation.objects.filter(translation__tr__contains=word)
        if words_obj:
            word_obj = sorted(words_obj, key=lambda x: x.translation["tr"].index(word))[0]
            words_dict_for_bot = {word_obj.word: {"translate": word_obj.translation}}
            return Response(words_dict_for_bot)
        else:
            word, trans = GooTrans().trans(word, dest='en')
            if trans:
                word_obj, created = Translation.objects.update_or_create(word=word, translation=trans, lang_key="eng_rus")
                if created:
                    add_audio(word_obj)
                words_dict_for_bot = {word_obj.word: {"translate": word_obj.translation}}
                return Response(words_dict_for_bot)
            else:
                return Response({"Слово не найдено"}, status=status.HTTP_404_NOT_FOUND)

    return Response({"Слово не найдено"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([OnlyBot])
def add_translate_word(request):

    en, ru = request.POST.get("en").lower(), (request.POST.getlist("ru"))
    word, created = Translation.objects.get_or_create(word=en)
    if created:
        word.translation = {'tr': list(map(lambda x: x.lower(), ru))}
        word.save()
    words_dict_for_bot = {word.word: {"translate": word.translation}}
    return Response(words_dict_for_bot)


@api_view(['POST'])
@permission_classes([OnlyBot])
def add_word_to_user(request):
    tg_id, word = request.POST.get("tg_id"), request.POST.get("word")
    user = AppUser(int(tg_id))
    word_obj = get_object_or_404(Translation, word=word)
    _, created = UsersWord.objects.get_or_create(bot_user=user.bot_user, word=word_obj, by_user=True)
    if not created:
        return Response("Word has been added before")
    return Response("Word has been added")
