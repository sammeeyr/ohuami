from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.catalog.models import Product, ProductVariant


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        RESTOCK = 'restock', _('Restock / Inward')
        SALE = 'sale', _('Customer Sale / Deducted')
        RETURN = 'return', _('Customer Return')
        ADJUSTMENT = 'adjustment', _('Inventory Adjustment')

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    quantity_change = models.IntegerField(help_text="Positive for restock/return, negative for sale/deduction")
    reference = models.CharField(max_length=150, blank=True, default='', help_text="e.g. Order #CT-20261028-1234")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = f"{self.product.name} ({self.variant.name if self.variant else 'Base'})"
        return f"{self.get_movement_type_display()} {self.quantity_change:+d} for {target}"
