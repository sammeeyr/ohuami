import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.catalog.models import Product, ProductVariant
from apps.promotions.models import Coupon


class Order(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PAID = 'paid', _('Paid')
        FAILED = 'failed', _('Failed')
        REFUNDED = 'refunded', _('Refunded')
        CANCELLED = 'cancelled', _('Cancelled')

    class FulfillmentStatus(models.TextChoices):
        UNFULFILLED = 'unfulfilled', _('Unfulfilled')
        PROCESSING = 'processing', _('Processing')
        SHIPPED = 'shipped', _('Shipped')
        DELIVERED = 'delivered', _('Delivered')
        RETURNED = 'returned', _('Returned')

    class OrderStatus(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        CONFIRMED = 'confirmed', _('Confirmed')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')

    order_reference = models.CharField(max_length=64, unique=True, editable=False, db_index=True)
    store = models.ForeignKey('catalog.Store', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Customer contact details snapshot
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)
    customer_name = models.CharField(max_length=255)

    # Shipping address snapshot
    shipping_recipient_name = models.CharField(max_length=255)
    shipping_phone = models.CharField(max_length=30)
    shipping_street_address = models.CharField(max_length=255)
    shipping_apartment = models.CharField(max_length=100, blank=True, default='')
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20, blank=True, default='')
    shipping_country = models.CharField(max_length=100, default='Nigeria')

    # Financial snapshots
    currency = models.CharField(max_length=10, default='NGN')
    items_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Promotion link
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    coupon_code_snapshot = models.CharField(max_length=50, blank=True, default='')

    # Statuses
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    fulfillment_status = models.CharField(max_length=20, choices=FulfillmentStatus.choices, default=FulfillmentStatus.UNFULFILLED)
    order_status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.CONFIRMED)

    # Payment details snapshot
    payment_method = models.CharField(max_length=50, default='paystack', help_text="e.g. paystack, flutterwave, sandbox")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_reference} ({self.customer_email})"

    @classmethod
    def generate_reference(cls):
        date_str = timezone.now().strftime('%Y%m%d')
        random_suffix = uuid.uuid4().hex[:6].upper()
        return f"CT-{date_str}-{random_suffix}"

    def save(self, *args, **kwargs):
        if not self.order_reference:
            self.order_reference = self.generate_reference()
        super().save(*args, **kwargs)

    @property
    def total_items_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def formatted_shipping_address(self):
        parts = [self.shipping_street_address]
        if self.shipping_apartment:
            parts.append(self.shipping_apartment)
        parts.append(f"{self.shipping_city}, {self.shipping_state}")
        if self.shipping_postal_code:
            parts.append(self.shipping_postal_code)
        parts.append(self.shipping_country)
        return ", ".join(parts)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')

    # Immutable historical snapshots
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=255, blank=True, default='')
    sku = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    product_image_url = models.CharField(max_length=500, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} in {self.order.order_reference}"
