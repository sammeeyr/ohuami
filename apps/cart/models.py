from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.catalog.models import Product, ProductVariant
from apps.promotions.models import Coupon


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='applied_carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        if self.user:
            return f"Cart of user {self.user.email}"
        return f"Guest Cart ({self.session_key})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def discount_amount(self):
        if self.coupon:
            is_valid, _ = self.coupon.is_valid(self.subtotal, self.user)
            if is_valid:
                return self.coupon.calculate_discount(self.subtotal)
        return Decimal('0.00')

    @property
    def total(self):
        sub = self.subtotal
        disc = self.discount_amount
        return max(Decimal('0.00'), sub - disc)

    @property
    def shipping_fee(self):
        return Decimal('2000.00')

    @property
    def total_with_shipping(self):
        return self.total + self.shipping_fee


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product', 'variant')
        ordering = ['created_at']

    def __str__(self):
        variant_info = f" - {self.variant.name}" if self.variant else ""
        return f"{self.quantity}x {self.product.name}{variant_info}"

    @property
    def unit_price(self):
        if self.variant and self.variant.price is not None:
            return self.variant.price
        return self.product.base_price

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    @property
    def is_available(self):
        if self.variant:
            return self.variant.stock_quantity >= self.quantity
        return self.product.available_stock >= self.quantity
