from django.shortcuts import render


# Create your views here.
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from bot_users.app_user import AppUser
from payments.models import Transaction
import hashlib

from web_langbot.permission import OnlyBot


@api_view(['POST'])
def rbk_notify(request):
    OutSum = request.POST["OutSum"]
    InvId = int(request.POST["InvId"])
    crc = request.POST["SignatureValue"]
    tr = Transaction.objects.get(id=InvId, amount=round(float(OutSum)))
    password2 = "removed"
    if crc.lower() == gen_hash(f"{OutSum}:{InvId}:{password2}") and tr.status == "CR":
        tr.status = Transaction.SUCCEEDED
        AppUser(tr.bot_user.tg_id).renew_subscription(tr.amount)
        tr.closed = now()
        tr.request_data = request.POST
        tr.save()
        return Response(f"OK{tr.id}")
    else:
        tr.status = Transaction.FAILED
    tr.closed = now()
    tr.request_data = request.POST
    tr.save()


@api_view(['POST'])
@permission_classes([OnlyBot])
def get_pay_link(request):
    tg_id, amount = int(request.POST["tg_id"]), int(request.POST["amount"])
    user = AppUser(tg_id)
    transaction = Transaction.objects.create(bot_user=user.bot_user, amount=amount)
    link = robokassa_link(transaction)
    return Response(link)


def robokassa_link(transaction):
    mrh_login = "TeachEnglish"
    out_summ = transaction.amount
    inv_id = transaction.id
    inv_desc = "Оплата подписки TeachEnglish"
    password1 = "removed"
    crc = gen_hash(f"{mrh_login}:{out_summ}:{inv_id}:{password1}")
    return f"https://auth.robokassa.ru/Merchant/Index.aspx?\
MerchantLogin={mrh_login}&\
OutSum={out_summ}&\
InvoiceID={inv_id}&\
Description={inv_desc}&\
SignatureValue={crc}"


def gen_hash(hash_str):
    hash = hashlib.md5()
    hash.update(hash_str.encode('utf-8'))
    return hash.hexdigest()
