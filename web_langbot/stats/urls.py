# api/urls.py
from django.urls import path
from stats import views

urlpatterns = [
    path('message_log/', views.message_log),
    path('call_log/', views.call_log),
    path('support_message/', views.support_message),
    path('support/', views.support_view),
    path('mailing/', views.mailing_view),
    path('mailing/send/<int:mail_id>', views.send_mail_view),
    path('daily/', views.daily_stats_view),
    path('emails.txt/', views.emails_txt),
    path('', views.stats_view)
]

