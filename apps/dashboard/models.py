import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.catalog.models import Store
from apps.orders.models import Order


class StoreAgent(models.Model):
    """Store staff members and support agents managed by the merchant."""
    class Role(models.TextChoices):
        MANAGER = 'manager', _('Store Manager')
        SUPPORT = 'support', _('Customer Support Agent')
        INVENTORY = 'inventory', _('Inventory Specialist')
        DISPATCH = 'dispatch', _('Dispatch & Logistics Coordinator')

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='agents')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='store_agent_profiles')
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, default='')
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.SUPPORT)
    is_active = models.BooleanField(default=True)
    
    # Granular Access Permissions
    can_manage_products = models.BooleanField(default=True)
    can_manage_orders = models.BooleanField(default=True)
    can_manage_dispatch = models.BooleanField(default=False)
    can_manage_customers = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Store Agent')
        verbose_name_plural = _('Store Agents')
        ordering = ['-created_at']
        unique_together = ('store', 'email')

    def __str__(self):
        return f"{self.name} ({self.get_role_display()}) — {self.store.name}"


class DispatchCarrier(models.Model):
    """Logistics partners and in-house delivery riders."""
    class CarrierType(models.TextChoices):
        IN_HOUSE = 'in_house', _('In-House Rider')
        THIRD_PARTY = 'third_party', _('Third-Party Courier (e.g. GIG, DHL, Fez)')
        FREIGHT = 'freight', _('Regional Freight / Haulage')

    class VehicleType(models.TextChoices):
        MOTORCYCLE = 'motorcycle', _('Motorcycle / Bike')
        VAN = 'van', _('Delivery Van')
        CAR = 'car', _('Sedan / Hatchback')
        TRUCK = 'truck', _('Delivery Truck')

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='carriers')
    name = models.CharField(max_length=150, help_text="Rider name or Courier Company (e.g. Ibrahim Sule, GIG Logistics)")
    carrier_type = models.CharField(max_length=30, choices=CarrierType.choices, default=CarrierType.IN_HOUSE)
    contact_person = models.CharField(max_length=150, blank=True, default='')
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True, default='')
    vehicle_type = models.CharField(max_length=30, choices=VehicleType.choices, default=VehicleType.MOTORCYCLE)
    vehicle_number = models.CharField(max_length=50, blank=True, default='', help_text="e.g. License plate: ABC-429-XY")
    service_areas = models.CharField(max_length=255, blank=True, default='Lagos, Abuja', help_text="Comma-separated coverage cities/zones")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Dispatch Carrier')
        verbose_name_plural = _('Dispatch Carriers')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_vehicle_type_display()})"


class DispatchShipment(models.Model):
    """Order dispatch tracking, assignment to couriers, and milestone progress."""
    class Status(models.TextChoices):
        PENDING_PICKUP = 'pending_pickup', _('Pending Pickup')
        PICKED_UP = 'picked_up', _('Picked Up')
        IN_TRANSIT = 'in_transit', _('In Transit')
        OUT_FOR_DELIVERY = 'out_for_delivery', _('Out for Delivery')
        DELIVERED = 'delivered', _('Delivered')
        FAILED_ATTEMPT = 'failed_attempt', _('Delivery Attempt Failed')
        RETURNED = 'returned', _('Returned to Merchant')

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='shipments')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipment')
    carrier = models.ForeignKey(DispatchCarrier, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipments')
    tracking_number = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING_PICKUP)
    
    pickup_address = models.CharField(max_length=255, blank=True, default='')
    delivery_address = models.CharField(max_length=255)
    recipient_name = models.CharField(max_length=150)
    recipient_phone = models.CharField(max_length=30)
    dispatch_notes = models.TextField(blank=True, default='', help_text="Special delivery instructions or gate codes")
    
    estimated_delivery = models.DateField(null=True, blank=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Dispatch Shipment')
        verbose_name_plural = _('Dispatch Shipments')
        ordering = ['-created_at']

    def __str__(self):
        return f"Shipment #{self.tracking_number} (Order #{self.order.order_reference})"

    @classmethod
    def generate_tracking_number(cls):
        date_str = timezone.now().strftime('%Y%m%d')
        suffix = uuid.uuid4().hex[:6].upper()
        return f"OHU-TRK-{date_str}-{suffix}"

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()
        super().save(*args, **kwargs)


class StoreCustomer(models.Model):
    """Customer relationship management record scoped to the merchant store."""
    class CustomerTag(models.TextChoices):
        NEW = 'new', _('New Customer')
        REGULAR = 'regular', _('Regular Buyer')
        VIP = 'vip', _('VIP Customer')
        WHOLESALE = 'wholesale', _('Wholesale Partner')

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='merchant_customers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='store_relationships')
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, default='')
    customer_tag = models.CharField(max_length=30, choices=CustomerTag.choices, default=CustomerTag.NEW)
    notes = models.TextField(blank=True, default='', help_text="Internal private notes on customer preferences")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Store Customer')
        verbose_name_plural = _('Store Customers')
        ordering = ['-created_at']
        unique_together = ('store', 'email')

    def __str__(self):
        return f"{self.name} ({self.email}) — {self.store.name}"

    @property
    def total_orders(self):
        return Order.objects.filter(store=self.store, customer_email__iexact=self.email).count()

    @property
    def total_spend(self):
        paid = Order.objects.filter(
            store=self.store,
            customer_email__iexact=self.email,
            payment_status=Order.PaymentStatus.PAID
        ).aggregate(models.Sum('total_amount'))['total_amount__sum']
        return paid or Decimal('0.00')

    @property
    def last_order(self):
        return Order.objects.filter(store=self.store, customer_email__iexact=self.email).order_by('-created_at').first()
