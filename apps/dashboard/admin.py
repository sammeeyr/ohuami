from django.contrib import admin
from .models import StoreAgent, DispatchCarrier, DispatchShipment, StoreCustomer


@admin.register(StoreAgent)
class StoreAgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'role', 'email', 'phone', 'is_active', 'created_at')
    list_filter = ('store', 'role', 'is_active')
    search_fields = ('name', 'email', 'phone', 'store__name')


@admin.register(DispatchCarrier)
class DispatchCarrierAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'carrier_type', 'vehicle_type', 'phone', 'is_active')
    list_filter = ('store', 'carrier_type', 'vehicle_type', 'is_active')
    search_fields = ('name', 'phone', 'email', 'store__name')


@admin.register(DispatchShipment)
class DispatchShipmentAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'order', 'store', 'carrier', 'status', 'recipient_name', 'estimated_delivery')
    list_filter = ('store', 'status', 'carrier')
    search_fields = ('tracking_number', 'order__order_reference', 'recipient_name', 'recipient_phone')


@admin.register(StoreCustomer)
class StoreCustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'store', 'phone', 'customer_tag', 'created_at')
    list_filter = ('store', 'customer_tag')
    search_fields = ('name', 'email', 'phone', 'store__name')
