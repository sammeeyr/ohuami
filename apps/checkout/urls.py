from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout_view, name='index'),
    path('process/', views.process_checkout, name='process'),
]
