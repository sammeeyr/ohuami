import json
import pytest
from decimal import Decimal
from django.urls import reverse
from apps.accounts.models import User, Address
from apps.catalog.models import Store, Product, Category, Brand
from apps.orders.models import Order, OrderItem
from apps.support.models import SupportEnquiry
from apps.reviews.models import Review
from apps.promotions.models import Coupon
from apps.cart.services import CartService


@pytest.fixture
def merchant_user(db):
    return User.objects.create_user(
        email="merchant_tester@example.com",
        password="MerchantPassword123!",
        first_name="Merchant",
        last_name="Owner",
        role=User.Role.MERCHANT,
    )


@pytest.fixture
def customer_user(db):
    return User.objects.create_user(
        email="shopper_tester@example.com",
        password="CustomerPassword123!",
        first_name="Shopper",
        last_name="Buyer",
        phone="08011223344",
        role=User.Role.CUSTOMER,
    )


@pytest.fixture
def other_customer_user(db):
    return User.objects.create_user(
        email="other_buyer@example.com",
        password="OtherPassword123!",
        role=User.Role.CUSTOMER,
    )


@pytest.fixture
def store_and_product(db, merchant_user):
    store = Store.objects.create(
        name="Lagos Tech Hub",
        slug="lagos-tech-hub",
        owner=merchant_user,
        status=Store.Status.ACTIVE,
        plan="Pro Plan",
    )
    category = Category.objects.create(name="Smartphones", slug="smartphones")
    brand = Brand.objects.create(name="TechPro", slug="techpro")
    product = Product.objects.create(
        store=store,
        category=category,
        brand=brand,
        name="Flagship Ultra 5G",
        slug="flagship-ultra-5g",
        base_price=Decimal("450000.00"),
        sku="TP-U5G-01",
        stock_quantity=25,
        is_active=True,
    )
    return store, product


@pytest.mark.django_db
def test_submit_product_review(client, customer_user, store_and_product):
    """Customer can submit product review via POST and view it on product page."""
    store, product = store_and_product
    client.force_login(customer_user)
    url = reverse('reviews:submit', kwargs={'product_id': product.id})

    payload = {
        'customer_name': 'Shopper Buyer',
        'rating': 5,
        'title': 'Outstanding Performance!',
        'comment': 'Fast delivery in Lagos and device is super fast and battery lasts 2 days.',
    }

    response = client.post(url, data=payload, follow=True)
    assert response.status_code == 200

    # Verify review in DB
    review = Review.objects.filter(product=product, user=customer_user).first()
    assert review is not None
    assert review.rating == 5
    assert review.title == 'Outstanding Performance!'

    # Check that product detail renders reviews
    pdp_url = reverse('catalog:product_detail', kwargs={'slug': product.slug})
    pdp_res = client.get(pdp_url)
    assert pdp_res.status_code == 200
    assert "Outstanding Performance!" in pdp_res.content.decode()


@pytest.mark.django_db
def test_support_contact_enquiry_form(client, customer_user):
    """Submitting support inquiry generates SupportEnquiry ticket and returns success confirmation."""
    url = reverse('support:contact')

    payload = {
        'name': 'Adaobi Okonjo',
        'email': 'adaobi@example.com',
        'phone': '+234 809 111 2233',
        'subject': 'Delivery Timeline to Port Harcourt',
        'message': 'Hello, I want to know the expected delivery duration to Rivers State before ordering.',
    }

    response = client.post(url, data=payload)
    assert response.status_code == 200
    content = response.content.decode()
    assert "Support Ticket Created Successfully!" in content
    assert "SUP-" in content

    # Verify database persistence
    enquiry = SupportEnquiry.objects.filter(email='adaobi@example.com').first()
    assert enquiry is not None
    assert enquiry.ticket_number.startswith('SUP-')
    assert enquiry.status == SupportEnquiry.Status.OPEN


@pytest.mark.django_db
def test_customer_profile_update_and_address_book(client, customer_user):
    """Customer can update their profile information and manage addresses."""
    client.force_login(customer_user)

    # 1. Update Profile
    update_url = reverse('accounts:update_profile')
    client.post(update_url, {
        'first_name': 'ShopperUpdated',
        'last_name': 'BuyerUpdated',
        'phone': '08099887766',
    })
    customer_user.refresh_from_db()
    assert customer_user.first_name == 'ShopperUpdated'
    assert customer_user.phone == '08099887766'

    # 2. Add New Address
    add_addr_url = reverse('accounts:add_address')
    client.post(add_addr_url, {
        'recipient_name': 'Shopper Office',
        'phone': '08099887766',
        'street_address': 'Plot 45 Admiralty Way',
        'apartment_suite': 'Suite 2B',
        'city': 'Lekki',
        'state': 'Lagos',
        'postal_code': '101233',
        'is_default': True,
    })
    address = Address.objects.filter(user=customer_user, city='Lekki').first()
    assert address is not None
    assert address.is_default is True

    # 3. Add second address and set it as default
    client.post(add_addr_url, {
        'recipient_name': 'Shopper Home',
        'phone': '08099887766',
        'street_address': '12 Victoria Island Crescent',
        'city': 'Lagos',
        'state': 'Lagos',
        'is_default': False,
    })
    addr2 = Address.objects.filter(user=customer_user, city='Lagos').first()
    assert addr2 is not None
    assert addr2.is_default is False

    # Set addr2 as default
    client.post(reverse('accounts:set_default_address', kwargs={'address_id': addr2.id}))
    addr2.refresh_from_db()
    address.refresh_from_db()
    assert addr2.is_default is True
    assert address.is_default is False

    # 4. Delete first address
    client.post(reverse('accounts:delete_address', kwargs={'address_id': address.id}))
    assert not Address.objects.filter(id=address.id).exists()


@pytest.mark.django_db
def test_order_detail_view_and_authorization(client, customer_user, other_customer_user, store_and_product):
    """Customer can view their order details with timeline; unauthorized customers are blocked."""
    store, product = store_and_product

    order = Order.objects.create(
        customer=customer_user,
        store=store,
        order_reference="CT-TEST-8899",
        customer_name="Shopper Buyer",
        customer_email=customer_user.email,
        customer_phone="08011223344",
        items_subtotal=Decimal("450000.00"),
        shipping_fee=Decimal("2000.00"),
        total_amount=Decimal("452000.00"),
        payment_status=Order.PaymentStatus.PAID,
        fulfillment_status=Order.FulfillmentStatus.SHIPPED,
        shipping_recipient_name="Shopper Buyer",
        shipping_phone="08011223344",
        shipping_street_address="12 Main St",
        shipping_city="Abuja",
        shipping_state="FCT",
        shipping_country="Nigeria",
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        product_name=product.name,
        unit_price=product.base_price,
        quantity=1,
        line_total=product.base_price,
    )

    detail_url = reverse('orders:detail', kwargs={'order_ref': order.order_reference})

    # Authorized customer access
    client.force_login(customer_user)
    response = client.get(detail_url)
    assert response.status_code == 200
    content = response.content.decode()
    assert "CT-TEST-8899" in content
    assert "Flagship Ultra 5G" in content
    assert "Dispatched" in content or "Fulfillment Tracking" in content

    # Other customer denied access
    client.force_login(other_customer_user)
    denied_response = client.get(detail_url)
    assert denied_response.status_code == 302
    assert denied_response.url == reverse('core:home')


@pytest.mark.django_db
def test_cart_coupon_application_and_removal(client, store_and_product):
    """Customer can apply and remove coupon in cart."""
    store, product = store_and_product

    coupon = Coupon.objects.create(
        code="SAVE10",
        discount_type=Coupon.DiscountType.PERCENTAGE,
        discount_value=Decimal("10.00"),
        min_order_value=Decimal("50000.00"),
        is_active=True,
    )

    # 1. Add item to cart
    client.post(reverse('cart:api_add'), data=json.dumps({
        'product_id': product.id,
        'quantity': 1,
    }), content_type='application/json')

    # 2. Apply valid coupon
    res = client.post(reverse('cart:api_apply_coupon'), data=json.dumps({
        'code': 'SAVE10',
    }), content_type='application/json')
    assert res.status_code == 200
    assert res.json()['success'] is True

    # Check cart detail displays discount
    cart_res = client.get(reverse('cart:detail'))
    assert cart_res.status_code == 200
    assert "SAVE10" in cart_res.content.decode()

    # 3. Remove coupon
    del_res = client.post(reverse('cart:api_remove_coupon'))
    assert del_res.status_code == 200
    assert del_res.json()['success'] is True


@pytest.mark.django_db
def test_merchant_dashboard_management_pages(client, merchant_user, store_and_product):
    """Merchant can manage products, create items, update orders, and adjust store settings."""
    store, product = store_and_product
    client.force_login(merchant_user)

    # 1. View merchant products list
    res_products = client.get(reverse('dashboard:products'))
    assert res_products.status_code == 200
    assert "Flagship Ultra 5G" in res_products.content.decode()

    # 2. Create new product
    category = Category.objects.first()
    res_create = client.post(reverse('dashboard:product_create'), data={
        'name': 'Wireless Charging Dock Pro',
        'category': category.id,
        'base_price': '18500.00',
        'sku': 'TP-WCD-01',
        'stock_quantity': 40,
        'description': 'Fast Qi certified 15W wireless charging dock.',
    }, follow=True)
    assert res_create.status_code == 200
    assert Product.objects.filter(store=store, sku='TP-WCD-01').exists()

    # 3. View merchant orders & update fulfillment status
    order = Order.objects.create(
        store=store,
        order_reference="CT-MERCH-001",
        customer_name="John Doe",
        customer_email="johndoe@example.com",
        customer_phone="08012345678",
        items_subtotal=Decimal("18500.00"),
        shipping_fee=Decimal("2000.00"),
        total_amount=Decimal("20500.00"),
        payment_status=Order.PaymentStatus.PAID,
        fulfillment_status=Order.FulfillmentStatus.UNFULFILLED,
        shipping_recipient_name="John Doe",
        shipping_phone="08012345678",
        shipping_street_address="Plot 5 Victoria Island",
        shipping_city="Lagos",
        shipping_state="Lagos",
    )
    res_orders = client.get(reverse('dashboard:orders'))
    assert res_orders.status_code == 200
    assert "CT-MERCH-001" in res_orders.content.decode()

    # Update status to processing
    res_status = client.post(
        reverse('dashboard:update_order_status', kwargs={'order_id': order.id}),
        data={'status': 'processing'},
        follow=True
    )
    assert res_status.status_code == 200
    order.refresh_from_db()
    assert order.fulfillment_status == Order.FulfillmentStatus.PROCESSING

    # 4. Update store settings
    res_settings = client.post(reverse('dashboard:settings'), data={
        'name': 'Lagos Tech Hub Enterprise',
        'tagline': 'Premium Tech & Computing Hub',
        'bank_name': 'Access Bank',
        'bank_account_number': '0123456789',
        'bank_account_name': 'Lagos Tech Hub Ltd',
        'payout_schedule': 'weekly',
    }, follow=True)
    assert res_settings.status_code == 200
    store.refresh_from_db()
    assert store.name == 'Lagos Tech Hub Enterprise'
    assert store.bank_account_number == '0123456789'

    # 5. Create promotional coupon
    res_coupon = client.post(reverse('dashboard:discounts'), data={
        'code': 'TECHDEAL15',
        'description': '15% off tech products',
        'discount_type': 'percentage',
        'discount_value': '15.00',
        'min_order_value': '20000.00',
        'usage_limit': '50',
    }, follow=True)
    assert res_coupon.status_code == 200
    assert Coupon.objects.filter(code='TECHDEAL15').exists()
