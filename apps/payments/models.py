from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.orders.models import Order


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SUCCESS = 'success', _('Success')
        FAILED = 'failed', _('Failed')
        REFUNDED = 'refunded', _('Refunded')

    class Gateway(models.TextChoices):
        PAYSTACK = 'paystack', _('Paystack')
        FLUTTERWAVE = 'flutterwave', _('Flutterwave')
        SANDBOX = 'sandbox', _('Sandbox / Demo Direct')

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    gateway = models.CharField(max_length=30, choices=Gateway.choices, default=Gateway.PAYSTACK)
    reference = models.CharField(max_length=120, unique=True, db_index=True)
    idempotency_key = models.CharField(max_length=120, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='NGN')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Gateway audit fields
    gateway_reference = models.CharField(max_length=120, blank=True, default='')
    raw_response = models.JSONField(default=dict, blank=True)
    channel = models.CharField(max_length=50, blank=True, default='', help_text="e.g. card, bank_transfer, ussd")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.reference} - {self.get_gateway_display()} - ₦{self.amount:,.2f} ({self.status})"
