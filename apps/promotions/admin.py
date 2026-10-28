from django.contrib import admin
from .models import Campaign, Coupon


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['title', 'badge_title', 'discount_label', 'start_date', 'end_date', 'is_active', 'display_order']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'display_order']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'min_order_value', 'times_used', 'usage_limit', 'is_active']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code', 'description']
