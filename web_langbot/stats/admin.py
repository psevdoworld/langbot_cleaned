from django.contrib import admin

# Register your models here.
from stats.models import SupportMessage, Mailing


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'message_id', 'username', 'text', 'reply', 'created', 'answered')
    search_fields = ('chat_id', 'username')
    list_filter = ('answered', )
    # def username(self, obj):
    #     return obj.message["from_user"]["username"]


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "created", "sended", "tested", "count_received")
