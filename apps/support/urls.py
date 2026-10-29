from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('', views.contact_view, name='index'),
    path('contact/', views.contact_view, name='contact'),
    path('api/chat/', views.api_chat, name='api_chat'),
]
