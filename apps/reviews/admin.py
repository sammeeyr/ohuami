from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'customer_name', 'rating', 'title', 'is_verified_purchase', 'is_moderated', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'is_moderated']
    search_fields = ['customer_name', 'product__name', 'comment']
    list_editable = ['is_moderated']
