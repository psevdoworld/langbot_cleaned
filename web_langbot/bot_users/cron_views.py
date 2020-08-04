from django.http import JsonResponse
from rest_framework.response import Response

from bot_users.models import BotUser

def zero_daily_rating(request):
    import pprint
    pprint.pprint(request.META)
    if request.META['SERVER_NAME'] == request.META['HTTP_HOST']:
        print("zero_daily_rating")
        BotUser.objects.filter().update(daily_rating=0)
        return JsonResponse({"response": "zero"})
    return JsonResponse({"response": "No no no, sorry"})
