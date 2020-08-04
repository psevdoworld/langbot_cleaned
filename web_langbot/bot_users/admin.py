from django.contrib import admin
from bot_users.models import BotUser
# Register your models here.

levels_str = {"начальный": "Beginner",
              "a1": "Elementary",
              "a2": "Pre-Intermediate",
              "b1": "Intermediate",
              "b2": "Upper-Intermediate",
              "c1": "Advanced",
              "c2": "Proficiency"
              }

@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'first_name', 'username', 'email', 'daily_rating', 'rating', 'ref_id',
                    'notify_time', '_level', 'allowed_date', 'last_action', 'date_join')
    search_fields = ('tg_id', 'username', 'email', 'ref_id')
    ordering = ('-last_action', )

    def _level(self, obj):
        return levels_str.get(obj.level, "Beginner")
