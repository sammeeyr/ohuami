from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('store/<slug:store_slug>/', views.storefront, name='storefront'),
    path('store/', views.storefront, name='storefront_default'),
    path('search/', views.search, name='search'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]
