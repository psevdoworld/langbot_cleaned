from django.contrib import admin
from payments.models import Transaction
# Register your models here.


@admin.register(Transaction)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'status', 'user_name', 'created', 'closed')
    search_fields = ('closed', )
    list_filter = ('status', 'amount')

    def user_name(self, obj):
        return obj.bot_user.username


admin.site.site_url = "/stats"
