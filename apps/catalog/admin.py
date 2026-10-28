from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Store, MerchantTier, Category, Brand, Product, ProductImage, ProductAttribute, ProductAttributeValue, ProductVariant


@admin.register(MerchantTier)
class MerchantTierAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'slug', 'monthly_price', 'commission_rate', 
        'max_products', 'max_staff_accounts', 'custom_domain_allowed', 
        'priority_support', 'is_active', 'display_order'
    ]
    list_editable = ['monthly_price', 'commission_rate', 'is_active', 'display_order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug', 'description']
    ordering = ['display_order', 'monthly_price']


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'owner_email', 'tier_badge', 'status_badge', 
        'bvn_verified', 'followers_count', 'storefront_link', 'created_at'
    ]
    list_filter = ['status', 'tier', 'verified_merchant', 'bvn_verified', 'is_active', 'payout_schedule']
    search_fields = ['name', 'slug', 'owner__email', 'owner__first_name', 'owner__last_name', 'bank_account_number']
    prepopulated_fields = {'slug': ('name',), 'subdomain': ('slug',)}
    actions = ['approve_selected_stores', 'suspend_selected_stores', 'verify_selected_bvn']

    fieldsets = (
        ('Store Identity', {
            'fields': ('name', 'slug', 'subdomain', 'owner', 'tagline', 'description', 'logo', 'banner_image')
        }),
        ('Multi-Merchant Tier & Status', {
            'fields': ('tier', 'plan', 'status', 'verified_merchant', 'is_active', 'verification_notes')
        }),
        ('Custom Domain Configuration', {
            'fields': ('custom_domain', 'custom_domain_verified'),
            'classes': ('collapse',),
        }),
        ('Payout & Banking Information', {
            'fields': ('bank_name', 'bank_account_number', 'bank_account_name', 'bvn_verified', 'payout_schedule'),
        }),
        ('Quotas & Commission Overrides', {
            'fields': ('commission_rate_override', 'max_products_limit', 'storage_quota_mb', 'followers_count'),
        }),
    )

    def owner_email(self, obj):
        return obj.owner.email
    owner_email.short_description = 'Merchant Owner'

    def tier_badge(self, obj):
        if obj.tier:
            return format_html('<span style="background:#FFC928; color:#111; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px;">{}</span>', obj.tier.name)
        return obj.plan
    tier_badge.short_description = 'Plan / Tier'

    def status_badge(self, obj):
        colors = {
            'active': '#10B981',
            'pending': '#F59E0B',
            'suspended': '#EF4444',
            'archived': '#6B7280'
        }
        color = colors.get(obj.status, '#111')
        return format_html('<span style="background:{}; color:#fff; padding:3px 8px; border-radius:12px; font-weight:bold; font-size:11px;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = 'Status'

    def storefront_link(self, obj):
        url = reverse('catalog:storefront', kwargs={'store_slug': obj.slug})
        return format_html('<a href="{}" target="_blank" style="color:#E53935; font-weight:bold;">View Store ↗</a>', url)
    storefront_link.short_description = 'Live Store'

    @admin.action(description="Approve and activate selected merchant stores")
    def approve_selected_stores(self, request, queryset):
        count = queryset.update(status=Store.Status.ACTIVE, verified_merchant=True, is_active=True)
        self.message_user(request, f"{count} merchant store(s) successfully verified and activated.")

    @admin.action(description="Suspend selected merchant stores")
    def suspend_selected_stores(self, request, queryset):
        count = queryset.update(status=Store.Status.SUSPENDED, is_active=False)
        self.message_user(request, f"{count} merchant store(s) suspended.")

    @admin.action(description="Mark selected merchant BVN as verified")
    def verify_selected_bvn(self, request, queryset):
        count = queryset.update(bvn_verified=True)
        self.message_user(request, f"{count} merchant bank account(s) verified.")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'display_order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['display_order', 'is_active']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'sku', 'category', 'base_price', 'stock_quantity', 'is_active', 'is_featured']
    list_filter = ['store', 'category', 'brand', 'is_active', 'is_featured', 'is_flash_sale']
    search_fields = ['name', 'sku', 'description', 'store__name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['base_price', 'is_active', 'is_featured']
    inlines = [ProductImageInline, ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'sku', 'price_override', 'stock_quantity', 'is_active']
    list_filter = ['is_active', 'product__category', 'product__store']
    search_fields = ['name', 'sku', 'product__name']


admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeValue)
admin.site.register(ProductImage)
