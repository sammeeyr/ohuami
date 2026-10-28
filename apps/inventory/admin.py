from django.contrib import admin
from .models import StockMovement


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'variant', 'movement_type', 'quantity_change', 'reference', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['product__name', 'reference']
