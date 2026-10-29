from django.urls import path
from . import views
from . import super_admin_views
from . import api_views

app_name = 'dashboard'

urlpatterns = [
    # Merchant Dashboard Core
    path('', views.dashboard_index, name='index'),

    # Products Management (Full CRUD)
    path('products/', views.merchant_products, name='products'),
    path('products/new/', views.merchant_product_create, name='product_create'),
    path('products/<int:product_id>/edit/', views.merchant_product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.merchant_product_delete, name='product_delete'),
    path('products/<int:product_id>/toggle-status/', views.merchant_product_toggle_status, name='product_toggle_status'),
    path('products/<int:product_id>/images/<int:image_id>/delete/', views.merchant_product_image_delete, name='product_image_delete'),
    path('products/<int:product_id>/images/<int:image_id>/primary/', views.merchant_product_image_set_primary, name='product_image_set_primary'),

    # Orders Management (Full CRUD)
    path('orders/', views.merchant_orders, name='orders'),
    path('orders/new/', views.merchant_order_create, name='order_create'),
    path('orders/<int:order_id>/', views.merchant_order_detail, name='order_detail'),
    path('orders/<int:order_id>/status/', views.merchant_update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/cancel/', views.merchant_order_cancel, name='order_cancel'),

    # Agents & Staff Management (Full CRUD)
    path('agents/', views.merchant_agents, name='agents'),
    path('agents/new/', views.merchant_agent_create, name='agent_create'),
    path('agents/<int:agent_id>/edit/', views.merchant_agent_edit, name='agent_edit'),
    path('agents/<int:agent_id>/delete/', views.merchant_agent_delete, name='agent_delete'),
    path('agents/<int:agent_id>/toggle-status/', views.merchant_agent_toggle_status, name='agent_toggle_status'),

    # Logistics & Dispatch Management (Full CRUD)
    path('logistics/', views.merchant_logistics, name='logistics'),
    path('logistics/carriers/new/', views.merchant_carrier_create, name='carrier_create'),
    path('logistics/carriers/<int:carrier_id>/edit/', views.merchant_carrier_edit, name='carrier_edit'),
    path('logistics/carriers/<int:carrier_id>/delete/', views.merchant_carrier_delete, name='carrier_delete'),
    path('logistics/dispatch/new/', views.merchant_dispatch_create, name='dispatch_create'),
    path('logistics/dispatch/<int:shipment_id>/status/', views.merchant_dispatch_update_status, name='dispatch_update_status'),

    # Customer Management (Full CRUD & CRM)
    path('customers/', views.merchant_customers, name='customers'),
    path('customers/new/', views.merchant_customer_create, name='customer_create'),
    path('customers/<int:customer_id>/', views.merchant_customer_detail, name='customer_detail'),
    path('customers/<int:customer_id>/delete/', views.merchant_customer_delete, name='customer_delete'),

    # CORS & Store Headless API Management
    path('api-cors/', views.merchant_api_cors, name='api_cors'),
    path('api-cors/regenerate-key/', views.merchant_api_regenerate_key, name='api_regenerate_key'),

    # Store Settings & Discounts
    path('settings/', views.merchant_settings, name='settings'),
    path('discounts/', views.merchant_discounts, name='discounts'),

    # CORS-Enabled RESTful Headless APIs
    path('api/products/', api_views.api_products_handler, name='api_products'),
    path('api/products/<int:pk>/', api_views.api_product_detail_handler, name='api_product_detail'),
    path('api/orders/', api_views.api_orders_handler, name='api_orders'),
    path('api/orders/<int:pk>/', api_views.api_order_detail_handler, name='api_order_detail'),
    path('api/logistics/', api_views.api_logistics_handler, name='api_logistics'),
    path('api/customers/', api_views.api_customers_handler, name='api_customers'),

    # Super Admin Control Center & APIs
    path('control-panel/', super_admin_views.super_admin_control_panel, name='super_admin_control_panel'),
    path('control-panel/api/update-merchant-status/', super_admin_views.api_update_merchant_status, name='api_update_merchant_status'),
    path('control-panel/api/update-global-settings/', super_admin_views.api_update_global_settings, name='api_update_global_settings'),
    path('control-panel/api/update-tier-config/', super_admin_views.api_update_tier_config, name='api_update_tier_config'),
    path('control-panel/api/toggle-service/', super_admin_views.api_toggle_service, name='api_toggle_service'),
]
