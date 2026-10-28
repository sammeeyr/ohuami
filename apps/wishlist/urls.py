from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.wishlist_list, name='list'),
    path('api/toggle/', views.api_toggle_wishlist, name='api_toggle'),
]
