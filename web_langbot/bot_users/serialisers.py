from django.utils import timezone
from rest_framework import serializers
from bot_users.models import BotUser


class BotUserSerializer(serializers.ModelSerializer):

    def to_representation(self, obj):
        tz = timezone.get_default_timezone()
        return {
            'tg_id': obj.tg_id,
            'first_name': obj.first_name,
            'username': obj.username,
            'email': obj.email,
            'notify_time': obj.notify_time,
            'level': obj.level,
            'ref_id': obj.ref_id,
            'allowed_date': timezone.localtime(obj.allowed_date, timezone=tz),

        }

    class Meta:
        model = BotUser
        fields = '__all__'

