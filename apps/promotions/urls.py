from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('flash-sale/', views.flash_sale_view, name='flash_sale'),
    path('coupons/', views.coupons_view, name='coupons'),
]
