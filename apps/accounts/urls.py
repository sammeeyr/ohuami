from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
    path('addresses/add/', views.add_address_view, name='add_address'),
    path('addresses/<int:address_id>/delete/', views.delete_address_view, name='delete_address'),
    path('addresses/<int:address_id>/set-default/', views.set_default_address_view, name='set_default_address'),
    path('password/change/', views.change_password_view, name='change_password'),
]
