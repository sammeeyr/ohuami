from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class StoreSetting(models.Model):
    # Platform Identity
    store_name = models.CharField(max_length=150, default='OHUAMI')
    parent_company = models.CharField(max_length=150, default='Cube Tech Enterprises')
    tagline = models.CharField(max_length=200, default='Your market. Your business. Your growth.')
    secondary_tagline = models.CharField(max_length=200, default='Commerce made for your ambition.')
    support_email = models.EmailField(default='support@ohuami.com')
    support_phone = models.CharField(max_length=30, default='+234 800 648 2642')
    whatsapp_support_phone = models.CharField(max_length=30, default='+234 801 234 5678')
    office_address = models.TextField(default='Plot 1204, Commercial District, Central Business District, Abuja, Nigeria')
    
    # Platform Commissions & Fee Defaults
    platform_commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5.00'), help_text="Default platform commission % on sales")
    platform_fixed_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('100.00'), help_text="Fixed transaction processing fee in NGN")
    payout_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('10000.00'), help_text="Minimum wallet balance for merchant automatic payout")
    payout_schedule_default = models.CharField(max_length=20, default='weekly')

    # Financial & Delivery defaults
    standard_shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2000.00'))
    free_shipping_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('100000.00'))
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text="e.g. 7.5 for VAT if applicable")
    default_currency = models.CharField(max_length=10, default='NGN')
    currency_symbol = models.CharField(max_length=5, default='₦')
    supported_currencies = models.JSONField(default=list, blank=True)

    # Multi-Merchant & Operational Controls
    maintenance_mode = models.BooleanField(default=False, help_text="Put storefronts in maintenance mode while preserving admin access")
    maintenance_message = models.TextField(default='OHUAMI is undergoing scheduled platform enhancements. We will be back online shortly.')
    allow_new_merchant_registration = models.BooleanField(default=True, help_text="Allow new vendors to onboard and register stores")
    require_kyc_verification = models.BooleanField(default=True, help_text="Require identity & bank account verification before activating store live transactions")
    allow_guest_checkout = models.BooleanField(default=True)
    default_store_storage_mb = models.PositiveIntegerField(default=1024)
    paystack_sandbox_mode = models.BooleanField(default=True, help_text="Force Paystack sandbox/mock mode")
    global_announcement = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        verbose_name = _('Global Store Setting')
        verbose_name_plural = _('Global Stores Settings')

    def __str__(self):
        return f"{self.store_name} Platform Settings"

    @classmethod
    def get_settings(cls):
        setting, _ = cls.objects.get_or_create(id=1)
        return setting


class PlatformService(models.Model):
    class Category(models.TextChoices):
        AI = 'ai', _('AI & Automation')
        CHANNELS = 'channels', _('Sales & Omnichannel')
        PAYMENTS = 'payments', _('Payments & Security')
        LOGISTICS = 'logistics', _('Logistics & Delivery')
        GROWTH = 'growth', _('Marketing & Growth')

    name = models.CharField(max_length=150)
    code = models.SlugField(max_length=100, unique=True, help_text="Unique identifier e.g. ai_automation, whatsapp_commerce")
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.AI)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, default='bolt', help_text="Icon identifier e.g. sparkle, chat, card, truck")
    is_global_enabled = models.BooleanField(default=True, help_text="Master toggle across entire platform")
    is_beta = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False, help_text="Requires paid tier")
    minimum_tier = models.ForeignKey('catalog.MerchantTier', on_delete=models.SET_NULL, null=True, blank=True, related_name='exclusive_services')
    config_schema = models.JSONField(default=dict, blank=True, help_text="Config parameters e.g. API keys, provider settings")
    enabled_stores = models.ManyToManyField('catalog.Store', blank=True, related_name='custom_enabled_services')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Feature & Service')
        verbose_name_plural = _('Features & Services')
        ordering = ['category', 'name']

    def __str__(self):
        status = "Active" if self.is_global_enabled else "Disabled"
        return f"{self.name} [{status}]"


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    target_model = models.CharField(max_length=100)
    target_id = models.CharField(max_length=100)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} on {self.target_model}:{self.target_id} at {self.created_at}"
