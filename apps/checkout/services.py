from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from apps.cart.models import Cart
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.inventory.models import StockMovement
from apps.core.models import StoreSetting


class CheckoutService:
    @staticmethod
    def calculate_checkout_totals(cart, shipping_state='FCT Abuja'):
        subtotal = cart.subtotal
        setting = StoreSetting.get_settings()

        # Shipping rules
        shipping_fee = Decimal('0.00')
        if subtotal > 0:
            if subtotal >= setting.free_shipping_threshold:
                shipping_fee = Decimal('0.00')
            else:
                shipping_fee = setting.standard_shipping_fee

        # Discount
        discount_amount = cart.discount_amount

        # VAT / Tax
        tax_amount = Decimal('0.00')
        if setting.tax_percentage > 0:
            tax_amount = round(((subtotal - discount_amount) * setting.tax_percentage) / Decimal('100.00'), 2)

        final_total = max(Decimal('0.00'), subtotal + shipping_fee - discount_amount + tax_amount)

        return {
            'subtotal': subtotal,
            'shipping_fee': shipping_fee,
            'discount_amount': discount_amount,
            'tax_amount': tax_amount,
            'final_total': final_total,
            'currency': setting.default_currency,
        }

    @staticmethod
    @transaction.atomic
    def create_order_from_cart(cart, customer_data, payment_method='paystack'):
        if not cart.items.exists():
            raise ValueError("Cannot checkout with an empty cart.")

        # 1. Server-side inventory re-validation
        for item in cart.items.select_for_update():
            available = item.variant.stock_quantity if item.variant else item.product.available_stock
            if item.quantity > available:
                target_name = f"{item.product.name} ({item.variant.name})" if item.variant else item.product.name
                raise ValueError(f"Insufficient stock for '{target_name}'. Only {available} available.")

        # 2. Server-side calculation of totals
        totals = CheckoutService.calculate_checkout_totals(cart, customer_data.get('state'))

        # 3. Create Order record
        order = Order.objects.create(
            customer=cart.user if cart.user else None,
            customer_email=customer_data['email'],
            customer_phone=customer_data['phone'],
            customer_name=customer_data['recipient_name'],
            shipping_recipient_name=customer_data['recipient_name'],
            shipping_phone=customer_data['phone'],
            shipping_street_address=customer_data['street_address'],
            shipping_city=customer_data['city'],
            shipping_state=customer_data['state'],
            shipping_country=customer_data.get('country', 'Nigeria'),
            items_subtotal=totals['subtotal'],
            shipping_fee=totals['shipping_fee'],
            discount_amount=totals['discount_amount'],
            tax_amount=totals['tax_amount'],
            total_amount=totals['final_total'],
            currency=totals['currency'],
            coupon=cart.coupon,
            coupon_code_snapshot=cart.coupon.code if cart.coupon else '',
            payment_status=Order.PaymentStatus.PENDING,
            payment_method=payment_method,
        )

        # 4. Create OrderItems & deduct stock atomically
        for item in cart.items.all():
            unit_price = item.unit_price
            line_total = unit_price * item.quantity
            img_url = ''
            if item.variant and item.variant.image:
                img_url = item.variant.image.image.url
            elif item.product.primary_image:
                img_url = item.product.primary_image.image.url

            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                product_name=item.product.name,
                variant_name=item.variant.name if item.variant else '',
                sku=item.variant.sku if item.variant else item.product.sku,
                unit_price=unit_price,
                quantity=item.quantity,
                line_total=line_total,
                product_image_url=img_url
            )

            # Deduct stock
            if item.variant:
                item.variant.stock_quantity = max(0, item.variant.stock_quantity - item.quantity)
                item.variant.save()
            else:
                item.product.stock_quantity = max(0, item.product.stock_quantity - item.quantity)
                item.product.save()

            # Record stock movement audit
            StockMovement.objects.create(
                product=item.product,
                variant=item.variant,
                movement_type=StockMovement.MovementType.SALE,
                quantity_change=-item.quantity,
                reference=f"Order #{order.order_reference}"
            )

        # If coupon was used, increment usage
        if cart.coupon:
            cart.coupon.times_used += 1
            cart.coupon.save()

        # Create pending Payment entry
        Payment.objects.create(
            order=order,
            gateway=payment_method,
            reference=order.order_reference,
            amount=order.total_amount,
            currency=order.currency,
            status=Payment.Status.PENDING,
        )

        return order
