from django.urls import path
from rest_framework.routers import DefaultRouter

from bot_users.views import BotUserViewSet, user_words_for_learning, change_word_status, get_user_dict, \
    get_word_to_repeat, change_repeat_word_status, words_from_topic_for_user,\
    user_words_for_test, referal_count, get_progress, add_rating, general_rating, words_from_topic_for_game, \
    general_daily_rating
from bot_users import cron_views
router = DefaultRouter()
router.register(r'user', BotUserViewSet, basename='user')
urlpatterns = router.urls


urlpatterns += [

    path('user_words_for_learning/<int:tg_id>/', user_words_for_learning),
    path('get_user_dict/<int:tg_id>/', get_user_dict),
    path('change_word_status/', change_word_status),
    path('change_repeat_word_status/', change_repeat_word_status),
    path('get_word_to_repeat/<int:tg_id>/', get_word_to_repeat),
    path('words_from_topic_for_user', words_from_topic_for_user),
    path('words_from_topic_for_game/', words_from_topic_for_game),
    path('user_words_for_test/<int:tg_id>/', user_words_for_test),
    path('referal_count/<int:tg_id>/', referal_count),
    path('<int:tg_id>/stats/', get_progress),
    path('add_rating/', add_rating),
    path('general_rating/', general_rating),
    path('general_daily_rating/', general_daily_rating),

    # for cron
    path("zero_daily_rating/", cron_views.zero_daily_rating)
]
