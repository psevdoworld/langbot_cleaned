from rest_framework import serializers
from DictionaryApp.models import Topics, Translation


class TranslationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Translation
        fields = '__all__'

class TopicsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topics
        fields = '__all__'
