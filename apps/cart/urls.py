from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='detail'),
    path('api/add/', views.api_add_to_cart, name='api_add'),
    path('api/update/', views.api_update_cart, name='api_update'),
    path('api/remove/', views.api_remove_from_cart, name='api_remove'),
    path('api/apply-coupon/', views.api_apply_coupon, name='api_apply_coupon'),
    path('api/remove-coupon/', views.api_remove_coupon, name='api_remove_coupon'),
]
