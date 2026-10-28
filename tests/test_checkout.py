import pytest
from decimal import Decimal
from apps.catalog.models import Product
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order
from apps.checkout.services import CheckoutService


@pytest.mark.django_db
def test_order_creation_and_stock_deduction(sample_product):
    variant = sample_product.variants.first()
    initial_stock = variant.stock_quantity
    assert initial_stock > 2

    cart = Cart.objects.create(session_key="test_checkout_session")
    CartItem.objects.create(cart=cart, product=sample_product, variant=variant, quantity=2)

    customer_data = {
        'recipient_name': 'Babatunde Fashola',
        'phone': '08098765432',
        'email': 'tunde@example.com',
        'street_address': 'Plot 400 Constitution Avenue',
        'city': 'Abuja',
        'state': 'FCT Abuja',
        'country': 'Nigeria'
    }

    order = CheckoutService.create_order_from_cart(cart, customer_data, payment_method='sandbox')
    
    assert order is not None
    assert order.order_reference.startswith("CT-")
    assert order.items.count() == 1
    assert order.items_subtotal == variant.price * 2
    assert order.total_amount > 0

    # Verify inventory was accurately deducted
    variant.refresh_from_db()
    assert variant.stock_quantity == initial_stock - 2


@pytest.mark.django_db
def test_out_of_stock_prevention(sample_category):
    product = Product.objects.create(
        name="Limited Supply Drone",
        slug="limited-drone",
        category=sample_category,
        base_price=Decimal("250000.00"),
        sku="DRONE-01",
        stock_quantity=1,
        is_active=True
    )

    cart = Cart.objects.create(session_key="out_of_stock_session")
    CartItem.objects.create(cart=cart, product=product, quantity=5)

    customer_data = {
        'recipient_name': 'Test User',
        'phone': '08011112222',
        'email': 'drone@example.com',
        'street_address': 'Street 1',
        'city': 'Lagos',
        'state': 'Lagos'
    }

    with pytest.raises(ValueError, match="Insufficient stock"):
        CheckoutService.create_order_from_cart(cart, customer_data, payment_method='sandbox')


@pytest.mark.django_db
def test_empty_cart_checkout_fails():
    cart = Cart.objects.create(session_key="empty_session")
    customer_data = {
        'recipient_name': 'Test User',
        'phone': '08011112222',
        'email': 'test@example.com',
        'street_address': 'Street 1',
        'city': 'Lagos',
        'state': 'Lagos'
    }

    with pytest.raises(ValueError, match="empty cart"):
        CheckoutService.create_order_from_cart(cart, customer_data)
