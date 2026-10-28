import pytest
from decimal import Decimal
from django.urls import reverse
from apps.catalog.models import Store, Product, Category
from apps.orders.models import Order
from apps.accounts.models import User


@pytest.mark.django_db
def test_screen_1_marketing_homepage(client):
    """Screen 1: Marketing Homepage has OHUAMI branding, 5 pillars, and CTAs."""
    response = client.get(reverse('core:home'))
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert "Your market." in content
    assert "Your business." in content
    assert "Your growth." in content
    assert "Start for Free" in content
    assert "Watch Demo" in content
    assert "Online Stores" in content
    assert "Inventory" in content
    assert "Orders & Payments" in content
    assert "Analytics" in content
    assert "Automation & AI" in content


@pytest.mark.django_db
def test_screen_2_merchant_dashboard(client):
    """Screen 2: Merchant Dashboard displays KPI metrics, order list, and store scoping."""
    # Seed Sunshine Fashion and Chinedu user
    chinedu = User.objects.create_user(
        email="chinedu_test@example.com",
        password="Password@123",
        first_name="Chinedu",
        last_name="Okafor",
        role=User.Role.MERCHANT
    )
    store = Store.objects.create(
        owner=chinedu,
        name="Sunshine Fashion",
        slug="sunshine-fashion",
        plan="Pro Plan",
        followers_count=1248
    )

    client.force_login(chinedu)
    response = client.get(reverse('dashboard:index'))
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert "Good morning, Chinedu!" in content
    assert "Sunshine Fashion" in content
    assert "Total Sales" in content
    assert "Total Orders" in content
    assert "Total Customers" in content
    assert "Sales Overview" in content


@pytest.mark.django_db
def test_screen_3_customer_storefront(client):
    """Screen 3: Customer Storefront renders brand header, category pills, and products."""
    store = Store.objects.filter(slug='sunshine-fashion').first()
    if not store:
        owner = User.objects.create_user(email="owner@test.com", password="Password@123")
        store = Store.objects.create(owner=owner, name="Sunshine Fashion", slug="sunshine-fashion")

    response = client.get(reverse('catalog:storefront', kwargs={'store_slug': 'sunshine-fashion'}))
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert "Sunshine Fashion" in content
    assert "Follow" in content
    assert "Style that" in content
    assert "Women" in content
    assert "Featured Products" in content


@pytest.mark.django_db
def test_screen_4_product_detail(client):
    """Screen 4: Product Detail renders Midi Dress, color swatches, size pills, and Buy Now CTA."""
    cat, _ = Category.objects.get_or_create(name="Women", slug="women")
    p, _ = Product.objects.get_or_create(
        slug="elegant-midi-dress",
        defaults={
            "name": "Elegant Midi Dress",
            "category": cat,
            "base_price": Decimal("28000.00"),
            "comparison_price": Decimal("35000.00"),
            "sku": "SF-DRS-001",
            "stock_quantity": 25,
            "badge_text": "-20%",
            "description": "A perfect blend of style and comfort."
        }
    )

    response = client.get(reverse('catalog:product_detail', kwargs={'slug': 'elegant-midi-dress'}))
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert "Elegant Midi Dress" in content
    assert "28,000" in content
    assert "Color" in content
    assert "Size" in content
    assert "Add to Cart" in content
    assert "Buy Now" in content


@pytest.mark.django_db
def test_screen_5_cart(client):
    """Screen 5: Cart details show line items, subtotal, shipping fee, and Proceed CTA."""
    response = client.get(reverse('cart:detail'))
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert "Your Cart" in content
    assert "Order Summary" in content
    assert "Proceed to Checkout" in content
    assert "Subtotal" in content
    assert "Shipping" in content


@pytest.mark.django_db
def test_screen_6_checkout(client, sample_product):
    """Screen 6: Checkout page renders shipping inputs, payment radios, order review, and Pay Now."""
    import json
    # Add item using client API
    add_resp = client.post(
        reverse('cart:api_add'),
        data=json.dumps({'product_id': sample_product.id, 'quantity': 1}),
        content_type='application/json'
    )
    assert add_resp.status_code == 200

    response = client.get(reverse('checkout:index'))
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert "Shipping Information" in content
    assert "Payment Method" in content
    assert "Order Summary" in content
    assert "Pay Now" in content
    assert "Visa, Mastercard, Verve" in content


@pytest.mark.django_db
def test_tenant_isolation(client):
    """Verify tenant isolation: Store A orders cannot be seen in Store B dashboard."""
    owner_a = User.objects.create_user(email="owner_a@test.com", password="Password@123", role=User.Role.MERCHANT)
    owner_b = User.objects.create_user(email="owner_b@test.com", password="Password@123", role=User.Role.MERCHANT)

    store_a = Store.objects.create(owner=owner_a, name="Store Alpha", slug="store-alpha")
    store_b = Store.objects.create(owner=owner_b, name="Store Beta", slug="store-beta")

    order_a = Order.objects.create(
        order_reference="OHU-ALPHA-01",
        store=store_a,
        total_amount=Decimal("50000.00"),
        customer_email="buyer_a@test.com",
        payment_status=Order.PaymentStatus.PAID
    )
    order_b = Order.objects.create(
        order_reference="OHU-BETA-01",
        store=store_b,
        total_amount=Decimal("12000.00"),
        customer_email="buyer_b@test.com",
        payment_status=Order.PaymentStatus.PAID
    )

    # Login as Store Alpha owner
    client.force_login(owner_a)
    response_a = client.get(reverse('dashboard:index'))
    content_a = response_a.content.decode('utf-8')
    assert "OHU-ALPHA-01" in content_a
    assert "OHU-BETA-01" not in content_a

    # Login as Store Beta owner
    client.force_login(owner_b)
    response_b = client.get(reverse('dashboard:index'))
    content_b = response_b.content.decode('utf-8')
    assert "OHU-BETA-01" in content_b
    assert "OHU-ALPHA-01" not in content_b
