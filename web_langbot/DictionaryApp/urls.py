# api/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from DictionaryApp.views import TopicsViewSet, TranslationViewSet, translate_by_word, add_word_to_user, add_translate_word
from DictionaryApp import service_views
router = DefaultRouter()

router.register(r'topics', TopicsViewSet)
router.register(r'translation', TranslationViewSet)

urlpatterns = router.urls

urlpatterns += [path('generate_oxford_5000/', service_views.generate_oxford_5000)]
urlpatterns += [path('create_oxford_topic/', service_views.create_oxford_topic)]

urlpatterns += [
    path('translate_by_word/<str:word>/', translate_by_word),
    path('add_word_to_user/', add_word_to_user),
    path('add_translate_word/', add_translate_word)
]
