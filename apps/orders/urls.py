from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('history/', views.order_history, name='history'),
    path('confirmation/<str:order_ref>/', views.order_confirmation, name='confirmation'),
    path('<str:order_ref>/', views.order_detail, name='detail'),
]
