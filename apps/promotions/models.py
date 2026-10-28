from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.catalog.models import Product, Category


class Campaign(models.Model):
    title = models.CharField(max_length=200, help_text="e.g. Kego Mega Flash")
    slug = models.SlugField(max_length=220, unique=True)
    badge_title = models.CharField(max_length=50, default='Flash Sale')
    subtitle = models.CharField(max_length=255, blank=True, default='')
    discount_label = models.CharField(max_length=50, default='Up to 50% OFF')
    banner_image = models.ImageField(upload_to='campaigns/', blank=True, null=True)
    bg_color = models.CharField(max_length=20, default='#FFC928', help_text="Hex color code for campaign card")
    text_color = models.CharField(max_length=20, default='#111111')
    button_text = models.CharField(max_length=50, default='Explore')
    button_link = models.CharField(max_length=255, default='#')
    products = models.ManyToManyField(Product, blank=True, related_name='campaigns')
    categories = models.ManyToManyField(Category, blank=True, related_name='campaigns')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')
        ordering = ['display_order', '-start_date']

    def __str__(self):
        return self.title

    @property
    def is_currently_running(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', _('Percentage (%)')
        FIXED = 'fixed', _('Fixed Amount (₦)')

    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True, default='')
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENTAGE)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    max_discount_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Max times this coupon can be used across all users")
    times_used = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(default=1)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')

    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()} ({self.discount_value})"

    def clean(self):
        if self.code:
            self.code = self.code.upper().strip()

    def is_valid(self, subtotal=Decimal('0.00'), user=None):
        now = timezone.now()
        if not self.is_active:
            return False, "This coupon is no longer active."
        if self.start_date and self.start_date > now:
            return False, "This coupon has not started yet."
        if self.end_date and self.end_date < now:
            return False, "This coupon has expired."
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False, "This coupon has reached its usage limit."
        if subtotal < self.min_order_value:
            return False, f"Minimum order amount for this coupon is ₦{self.min_order_value:,.2f}."
        return True, "Valid coupon."

    def calculate_discount(self, subtotal):
        if subtotal <= 0:
            return Decimal('0.00')
        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount = (subtotal * self.discount_value) / Decimal('100.00')
            if self.max_discount_amount and discount > self.max_discount_amount:
                discount = self.max_discount_amount
            return round(discount, 2)
        elif self.discount_type == self.DiscountType.FIXED:
            discount = min(self.discount_value, subtotal)
            return round(discount, 2)
        return Decimal('0.00')
