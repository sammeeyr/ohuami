from django.contrib import admin
from django.utils.html import format_html
from .models import StoreSetting, PlatformService, AuditLog


admin.site.site_header = "OHUAMI Super Admin — Cube Tech Enterprises"
admin.site.site_title = "OHUAMI Platform Control Panel"
admin.site.index_title = "Platform Management & Multi-Store Control"


@admin.register(StoreSetting)
class StoreSettingAdmin(admin.ModelAdmin):
    list_display = [
        'store_name', 'parent_company', 'platform_commission_percent', 
        'standard_shipping_fee', 'free_shipping_threshold', 
        'maintenance_status', 'allow_new_merchant_registration'
    ]

    fieldsets = (
        ('Platform Global Identity', {
            'fields': (
                'store_name', 'parent_company', 'tagline', 'secondary_tagline',
                'support_email', 'support_phone', 'whatsapp_support_phone', 'office_address'
            )
        }),
        ('Platform Commissions & Fees', {
            'fields': (
                'platform_commission_percent', 'platform_fixed_fee', 
                'payout_threshold', 'payout_schedule_default'
            )
        }),
        ('Delivery & Currency Defaults', {
            'fields': (
                'standard_shipping_fee', 'free_shipping_threshold', 
                'tax_percentage', 'default_currency', 'currency_symbol', 'supported_currencies'
            )
        }),
        ('Multi-Merchant & Operational Controls', {
            'fields': (
                'maintenance_mode', 'maintenance_message',
                'allow_new_merchant_registration', 'require_kyc_verification',
                'allow_guest_checkout', 'default_store_storage_mb',
                'paystack_sandbox_mode', 'global_announcement'
            )
        }),
    )

    def maintenance_status(self, obj):
        if obj.maintenance_mode:
            return format_html('<span style="background:#EF4444; color:#fff; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px;">MAINTENANCE ON</span>')
        return format_html('<span style="background:#10B981; color:#fff; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px;">LIVE</span>')
    maintenance_status.short_description = 'System Status'


@admin.register(PlatformService)
class PlatformServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'status_badge', 'is_premium', 'minimum_tier', 'updated_at']
    list_filter = ['category', 'is_global_enabled', 'is_premium', 'minimum_tier']
    list_editable = []
    search_fields = ['name', 'code', 'description']
    filter_horizontal = ['enabled_stores']
    actions = ['enable_selected_services', 'disable_selected_services']

    fieldsets = (
        ('Service Definition', {
            'fields': ('name', 'code', 'category', 'icon', 'description')
        }),
        ('Service Availability & Gating', {
            'fields': ('is_global_enabled', 'is_beta', 'is_premium', 'minimum_tier')
        }),
        ('Store Customization & Config', {
            'fields': ('enabled_stores', 'config_schema'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        if obj.is_global_enabled:
            return format_html('<span style="background:#10B981; color:#fff; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px;">ACTIVE</span>')
        return format_html('<span style="background:#6B7280; color:#fff; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px;">DISABLED</span>')
    status_badge.short_description = 'Global Status'

    @admin.action(description="Enable selected services across the platform")
    def enable_selected_services(self, request, queryset):
        count = queryset.update(is_global_enabled=True)
        self.message_user(request, f"{count} platform service(s) enabled.")

    @admin.action(description="Disable selected services globally")
    def disable_selected_services(self, request, queryset):
        count = queryset.update(is_global_enabled=False)
        self.message_user(request, f"{count} platform service(s) disabled.")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'target_model', 'target_id', 'user', 'created_at']
    list_filter = ['action', 'target_model', 'created_at']
    search_fields = ['action', 'target_model', 'target_id']
    readonly_fields = ['user', 'action', 'target_model', 'target_id', 'details', 'ip_address', 'created_at']
