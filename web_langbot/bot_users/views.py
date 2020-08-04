from django.http import JsonResponse
from django.shortcuts import render
from datetime import timedelta, datetime
from django.utils.timezone import now
from math import ceil
# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from DictionaryApp.models import Translation, UsersWord
import random

from DictionaryApp.serialisers import TranslationSerializer
from bot_users.app_user import AppUser
from bot_users.models import BotUser, LEVELS
from bot_users.serialisers import BotUserSerializer
from bot_users.utils import user_add_days
from web_langbot.permission import OnlyBot
HOW_MUCH_WORD = 5
HOW_MUCH_WORD_GAME = 10


class BotUserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    permission_classes = [OnlyBot]
    serializer_class = BotUserSerializer
    queryset = BotUser.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notify_time', ]


    def perform_create(self, serializer):
        serializer.save()

        if serializer.data["ref_id"]:
            first_level = BotUser.objects.filter(tg_id=serializer.data["ref_id"]).first()
            user_add_days(first_level, 5)
            if first_level.ref_id:
                second_level = BotUser.objects.filter(tg_id=first_level.ref_id).first()
                user_add_days(second_level, 1)

@api_view(['GET'])
@permission_classes([OnlyBot])
def referal_count(request, tg_id):
    firsts = BotUser.objects.filter(ref_id=tg_id)
    firsts_count = firsts.count()
    seconds_count = sum([BotUser.objects.filter(ref_id=i.tg_id).count() for i in firsts])
    return Response([firsts_count, seconds_count])


@api_view(['GET'])
@permission_classes([OnlyBot])
def user_words_for_learning(request, tg_id):
    user = AppUser(tg_id)
    words_for_learning = UsersWord.objects.filter(bot_user=user.bot_user, learned=False).all()
    amount_words_for_learning = UsersWord.objects.filter(bot_user=user.bot_user, learned=False).count()
    words_id = [word.word.id for word in words_for_learning[:HOW_MUCH_WORD]]
    if amount_words_for_learning < 5:
        words_for_learning = five_random_words(user.bot_user, HOW_MUCH_WORD - amount_words_for_learning)
        words_id += [word.word.id for word in words_for_learning[:HOW_MUCH_WORD]]

    words = Translation.objects.filter(id__in=words_id)
    words_dict_for_bot = {word.word: {"translate": word.translation, "audio": str(word.audio)} for word in words}
    print(*[i.id for i in words])
    print(*[i.word for i in words])
    return Response(words_dict_for_bot)


@api_view(['GET'])
@permission_classes([OnlyBot])
def words_from_topic_for_user(request):
    tg_id, topic = request.GET.get("tg_id"), request.GET.get("topic")
    user = AppUser(tg_id)
    users_words = [word.word.id for word in UsersWord.objects.filter(bot_user=user.bot_user, learned=True)]
    topic_words = Translation.objects.filter(topics__id=topic).exclude(id__in=users_words).exclude(translation={})
    if topic_words:
        words_dict_for_bot = {word.word: {"translate": word.translation, "audio": str(word.audio)} for word in topic_words[:HOW_MUCH_WORD]}
        return Response(words_dict_for_bot)
    return Response("Вы выучили все слова в этом топике!")


@api_view(['GET'])
@permission_classes([OnlyBot])
def words_from_topic_for_game(request):
    topic = request.GET.get("topic")
    words_id = random.sample([word.id
                              for word in Translation.objects.filter(topics__id=topic).exclude(translation={})], 10)
    words = Translation.objects.filter(id__in=words_id)
    words_dict_for_bot = {word.word: {"translate": word.translation} for word in words[:HOW_MUCH_WORD_GAME]}
    return Response(words_dict_for_bot)



@api_view(['POST'])
@permission_classes([OnlyBot])
def change_word_status(request):
    tg_id, word = request.POST.get("tg_id"), request.POST.get("word")
    user = AppUser(int(tg_id))
    word = get_object_or_404(Translation, word=word)
    user_word, created = UsersWord.objects.get_or_create(bot_user=user.bot_user, word=word)
    user_word.learned = True
    user_word.count_days = 1
    user_word.learned_date = now()
    user_word.when_repeat = now()
    user_word.save()
    return Response("Words status changed")


@api_view(['GET'])
@permission_classes([OnlyBot])
def get_user_dict(request, tg_id):
    page = int(request.GET["page"])
    user = AppUser(int(tg_id))
    words = UsersWord.objects.filter(bot_user=user.bot_user)\
                             .filter(Q(learned=True) | Q(by_user=True))\
                             .order_by('word__word')
    all_page = ceil(len(words) / 10)
    index = 10 * (page - 1)
    end_index = 9 if len(words) - index > 10 else len(words) - index
    words = words[index:index + end_index + 1]
    print(all_page)
    print(*[word.word.word for word in words])
    curr_page_words = {word.word.word: {"translate": word.word.translation} for word in words}
    return Response({"words": curr_page_words, "pages": all_page})


@api_view(['GET'])
@permission_classes([OnlyBot])
def get_word_to_repeat(request, tg_id):
    user = AppUser(tg_id)
    word = user.word_to_repeat()
    if word:
        serializer = TranslationSerializer(word)
        return Response(serializer.data)
    return Response("There are no more words for today")


@api_view(['POST'])
@permission_classes([OnlyBot])
def change_repeat_word_status(request):
    tg_id, word_id, mem_status = request.POST.get("tg_id"), request.POST.get("word_id"), request.POST.get("mem_status")
    user = AppUser(tg_id)
    user.change_repeat_word_status(word_id, mem_status)
    return Response("Status changed")


@api_view(['GET'])
@permission_classes([OnlyBot])
def user_words_for_test(request, tg_id):
    user = AppUser(tg_id)
    level = LEVELS[user.bot_user.level] if user.bot_user.level else "a1"
    words_id = random.sample(
        [word.id for word in Translation.objects.filter(oxford_level=level).exclude(translation={})],
        20)
    words = Translation.objects.filter(id__in=words_id)
    words_dict_for_bot = {word.word: {"translate": word.translation} for word in words}
    return Response(words_dict_for_bot)


@api_view(['GET'])
@permission_classes([OnlyBot])
def get_progress(request, tg_id):
    user = AppUser(int(tg_id))
    stats = user.stats()
    return Response(stats)


@api_view(['GET'])
@permission_classes([OnlyBot])
def general_rating(request):
    data = BotUser.objects.all().order_by('-rating')[:10]
    data = [(user.first_name, user.rating) for user in data]
    return Response(data)

@api_view(['GET'])
@permission_classes([OnlyBot])
def general_daily_rating(request):
    data = BotUser.objects.all().order_by('-daily_rating')[:10]
    data = [(user.first_name, user.daily_rating) for user in data]
    return Response(data)


@api_view(['POST'])
@permission_classes([OnlyBot])
def add_rating(request):
    tg_id, count = request.POST.get("tg_id"), request.POST.get("count"),
    user = AppUser(int(tg_id))
    stats = user.add_rating(int(count))
    return Response()

def five_random_words(bot_user, n = None):
    all_words = [word.word.id for word in UsersWord.objects.filter(bot_user=bot_user).all()]
    words_id = random.sample([word.id for word in Translation.objects.exclude(id__in=all_words).exclude(translation={})],
                          n or HOW_MUCH_WORD)
    words = Translation.objects.filter(id__in=words_id)
    for word in words:
        UsersWord.objects.get_or_create(bot_user=bot_user, word=word, by_user=False, learned=False)

    return UsersWord.objects.filter(bot_user=bot_user, learned=False).all()
