from django.urls import path
from rest_framework.routers import DefaultRouter
from payments import views

urlpatterns = [
    path('get_pay_link/', views.get_pay_link),
    path('rbk/notify/', views.rbk_notify),
]
