from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'variant_name', 'sku', 'unit_price', 'quantity', 'line_total']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_reference', 'customer_name', 'customer_email', 'total_amount', 'payment_status', 'fulfillment_status', 'created_at']
    list_filter = ['payment_status', 'fulfillment_status', 'created_at', 'payment_method']
    search_fields = ['order_reference', 'customer_name', 'customer_email', 'customer_phone']
    readonly_fields = ['order_reference', 'created_at', 'updated_at', 'paid_at']
    inlines = [OrderItemInline]
