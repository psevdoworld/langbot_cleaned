import datetime
import json
import telebot
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.db.models import Sum
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import redirect
from bot_users.models import BotUser
from payments.models import Transaction
from stats.models import SupportMessage, Mailing
from web_langbot.permission import OnlyBot
from web_langbot.settings import ADMINS_ID
from .tasks import send_spam

@api_view(['POST'])
@permission_classes([OnlyBot])
def message_log(request):
    # print(request.POST["message"])
    return Response()


@api_view(['POST'])
@permission_classes([OnlyBot])
def call_log(request):
    # print(request.POST["call"])
    return Response()


def emails_txt(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            file_data = ("\n".join([user.email for user in BotUser.objects.filter() if user.email]))
            response = HttpResponse(file_data, content_type='application/text charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="emails.txt"'
            return response


def mailing_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        # data = generate_statistic()
        if request.method == "GET":
            data = Mailing.objects.all().order_by("created")
            return render(request, "spam.html",
                          context={"data": data, "user": request.user, "s_user": request.user.is_superuser, "title": "Рассылка"})
        elif request.method == "POST":
            print(request.POST)
            if request.POST["id"]:
                Mailing.objects.filter(id=int(request.POST["id"])).update(text=request.POST["text"])
            elif request.POST["id"] == "":
                mail = Mailing.objects.create(text=request.POST["text"])
            return redirect("/stats/mailing")
    elif request.user.is_authenticated and not request.user.is_superuser:
        return redirect("/stats/support")
    else:
        return redirect("/admin/login/?next=/stats/")


def send_mail_view(request, mail_id):
    if request.GET["type"] in ["test", "for_all"]:
        send_spam.delay(type_spam=request.GET["type"], mail_id=mail_id)
    return redirect("/stats/mailing")


@api_view(['POST'])
@permission_classes([OnlyBot])
def support_message(request):
    data_json = request.POST["message"]
    try:
        data_json = json.loads(data_json.replace("'", '"').replace("False", "false").replace("None", "null"))
    except Exception as e:
        print(e)
    SupportMessage.objects.create(
        chat_id=int(request.POST["chat_id"]),
        username=request.POST.get("user_name", ""),
        message_id=int(request.POST["message_id"]),
        text=request.POST["text"],
        message=data_json
    )
    return Response()


@require_http_methods(["GET"])
def stats_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        data = generate_statistic()
        return render(request, "dashboard.html", context={"data": data,
                                                          "user": request.user,
                                                          "s_user": request.user.is_superuser,
                                                          "title": "Общая статистика"})
    elif request.user.is_authenticated and not request.user.is_superuser:
        return redirect("/stats/support")
    else:
        return redirect("/admin/login/?next=/stats/")


@require_http_methods(["GET"])
def daily_stats_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        date = request.GET["date"] if request.GET.get("date") else datetime.datetime.now().date().isoformat()
        # _date = datetime.datetime.fromisoformat(date) # py 3.8
        _date = datetime.datetime.strptime(date, "%Y-%m-%d")
        data = gen_daily_statistic(_date)
        return render(request, "daily.html", context={"data": data,
                                                      "user": request.user,
                                                      "s_user": request.user.is_superuser,
                                                      "title": f"Статистика на {date}"})
    elif request.user.is_authenticated and not request.user.is_superuser:
        return redirect("/stats/support")
    else:
        return redirect("/admin/login/?next=/stats/")


def gen_daily_statistic(_date):
    transactions = Transaction.objects.filter
    user_filter = BotUser.objects.filter
    data = {
        "transaction": {
            "one_m": transactions(amount=159, closed__date=_date).count(),
            "tree_m": transactions(amount=299, closed__date=_date).count(),
            "year": transactions(amount=990, closed__date=_date).count(),
            "sum": transactions(closed__date=_date).aggregate(Sum('amount'))['amount__sum'] or 0
        },
        "users": {
            "register": user_filter(date_join__date=_date).count(),
            "used": user_filter(last_action__date=_date).count()
        }
    }
    return data




def generate_statistic():
    today = datetime.datetime.now().date()
    delta = datetime.timedelta
    user_filter = BotUser.objects.filter
    transactions = Transaction.objects.filter
    data = {
        "register":
            {
                "last_month": user_filter(date_join__date__gt=today-delta(30)).count(),
                "last_week": user_filter(date_join__date__gt=today-delta(7)).count(),
                "today": user_filter(date_join__date=today).count()
            },
        "used":
            {
                "last_month": user_filter(last_action__date__gt=today - delta(30)).count(),
                "last_week": user_filter(last_action__date__gt=today - delta(7)).count(),
                "today": user_filter(last_action__date=today).count()
            },

        "another": {
            "all_user": user_filter().count(),
            "not_active": user_filter(last_action__date__lt=today - delta(7)).count(),
            "subscribe": user_filter(allowed_date__date__gt=today).count(),
            "average_life": get_average(user_filter(last_action__date__lt=today - delta(7))),
            "count_referal": user_filter(ref_id__isnull=False).count(),
        },
        "transaction": {
            "last_month": {
                "one_m": transactions(amount=159, closed__date__gt=today-delta(30)).count(),
                "tree_m": transactions(amount=299, closed__date__gt=today-delta(30)).count(),
                "year": transactions(amount=990, closed__date__gt=today-delta(30)).count(),
                "sum": transactions(closed__date__gt=today-delta(30)).aggregate(Sum('amount'))['amount__sum'] or 0
            },
            "last_week": {
                "one_m": transactions(amount=159, closed__date__gt=today - delta(7)).count(),
                "tree_m": transactions(amount=299, closed__date__gt=today - delta(7)).count(),
                "year": transactions(amount=990, closed__date__gt=today - delta(7)).count(),
                "sum": transactions(closed__date__gt=today - delta(7)).aggregate(Sum('amount'))['amount__sum'] or 0
            },
            "today": {
                "one_m": transactions(amount=159, closed__date=today).count(),
                "tree_m": transactions(amount=299, closed__date=today).count(),
                "year": transactions(amount=990, closed__date=today).count(),
                "sum": transactions(closed__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
            },

        },
        "chart_register": {
            "labels": [date for date in [(today-delta(i)).strftime("%d.%m") for i in range(30, -1, -1)]],
            "series": [
                [user_filter(date_join__date=today - delta(day)).count() for day in [i for i in range(30, -1, -1)]]
            ]
        },
        "chart_action": {
            "labels": [date for date in [(today - delta(i)).strftime("%d.%m") for i in range(30, -1, -1)]],
            "series": [
                [user_filter(last_action__date=today - delta(day)).count() for day in [i for i in range(30, -1, -1)]]
            ]
        },
        "top_rating": {
            "all": [(user.first_name, user.rating) for user in BotUser.objects.all().order_by('-rating')[:10]],
            "day": [(user.first_name, user.daily_rating) for user in  BotUser.objects.all().order_by('-daily_rating')[:10]]
        },
        "referal":  get_top_referal(user_filter().all())

    }
    return data
def get_top_referal(users):
    data = {}
    for user in users:
        name = user.first_name or user.username or user.tg_id
        data[name] = BotUser.objects.filter(ref_id=user.tg_id).count()
    data = sorted(data.items(), key=lambda i: -i[1])[:10]
    return data




def get_average(users):
    if users:
        _sum = 0
        for user in users:
            _sum += (user.last_action - user.date_join).days
        return round(_sum / len(users))
    return 0




@require_http_methods(["GET", "POST"])
def support_view(request):
    # data = generate_statistic()
    if request.user.is_authenticated:
        # data = generate_statistic()
        if request.method == "GET":
            messages = SupportMessage.objects.filter(answered=False).order_by("-created")
            return render(request, "support.html", context={"messages": messages,
                                                            "user": request.user,
                                                          "s_user": request.user.is_superuser,
                                                          "title": "Поддержка"})
        elif request.method == "POST":
            print(request.POST)
            relpy_message(int(request.POST["id"]), request.POST["reply"])
            messages = SupportMessage.objects.filter(answered=False).order_by("-created")
            return redirect("/stats/support")

    else:
        return redirect("/admin/login/?next=/stats/")


def relpy_message(id, text):
    message = SupportMessage.objects.filter(id=id).first()
    try:
        m_text = "*Ответ на сообщение в поддержку:*"
        m_text += f"\n\n{text}"
        m_text += "\n\n_С уважением, команда English Bot_"
        tb = telebot.TeleBot("1218756232:AAH8B9zQeZWS56IfW3_vIeiuc_YpU8s6D-w")
        ret_msg = tb.send_message(message.chat_id, m_text, reply_to_message_id=message.message_id, parse_mode="Markdown")
        message.answered = True
        message.reply = text
        message.save()
    except Exception as e:
        print(e)
        raise Exception("Не смог отправить сообщение в поддержку")
