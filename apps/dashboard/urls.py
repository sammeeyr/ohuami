from django.urls import path
from . import views
from . import super_admin_views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('control-panel/', super_admin_views.super_admin_control_panel, name='super_admin_control_panel'),
    path('control-panel/api/update-merchant-status/', super_admin_views.api_update_merchant_status, name='api_update_merchant_status'),
    path('control-panel/api/update-global-settings/', super_admin_views.api_update_global_settings, name='api_update_global_settings'),
    path('control-panel/api/update-tier-config/', super_admin_views.api_update_tier_config, name='api_update_tier_config'),
    path('control-panel/api/toggle-service/', super_admin_views.api_toggle_service, name='api_toggle_service'),
]
