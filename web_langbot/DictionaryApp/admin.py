from django.contrib import admin

from DictionaryApp.models import Topics, Translation, UsersWord


@admin.register(UsersWord)
class UsersWordAdmin(admin.ModelAdmin):
    list_display = ('bot_user', '_word', 'by_user', 'learned', 'count_days', 'when_repeat')
    list_filter = ('learned', 'by_user')
    search_fields = ['bot_user__tg_id']

    def _word(self, obj):
        return f"{obj.word.id} {obj.word.word}"


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('word', 'lang_key', 'pos', 'translation', 'oxford_level', 'audio')
    list_filter = ('oxford_level', 'pos')
    search_fields = ['word']


@admin.register(Topics)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'available', 'image')
    list_filter = ('available',)
    search_fields = ['name']
    # list_filter = ('learned', 'by_user')
    # search_fields = ['word']
# admin.site.register()
# admin.site.register(Translation)
