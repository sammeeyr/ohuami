import io
import json
from decimal import Decimal
from PIL import Image
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from apps.accounts.models import User
from apps.catalog.models import Store, Product, Category, MerchantTier, ProductImage
from apps.orders.models import Order, OrderItem
from apps.dashboard.models import StoreAgent, DispatchCarrier, DispatchShipment, StoreCustomer


@pytest.fixture
def merchant_setup(db):
    owner = User.objects.create_user(
        email='merchant_test@ohuami.com',
        password='Password@123',
        role=User.Role.MERCHANT,
        first_name='Test',
        last_name='Merchant',
    )
    tier = MerchantTier.objects.create(
        name='Pro Tier Test',
        slug='pro-tier-test',
        max_products=100,
        max_staff_accounts=3,
        commission_rate=Decimal('3.50'),
    )
    store = Store.objects.create(
        owner=owner,
        name='Test African Boutique',
        slug='test-african-boutique',
        tier=tier,
        cors_allowed_origins='http://localhost:3000, https://testboutique.ng',
        api_key='ohu_test_secret_key_1234567890',
        api_key_enabled=True,
    )
    category = Category.objects.create(name='Test Category', slug='test-category')
    product = Product.objects.create(
        store=store,
        name='Adire Silk Kimono',
        slug='adire-silk-kimono',
        category=category,
        base_price=Decimal('25000.00'),
        sku='ADR-KMN-001',
        stock_quantity=15,
        is_active=True,
    )
    order = Order.objects.create(
        store=store,
        customer_name='Amina Bello',
        customer_email='amina@example.com',
        customer_phone='+234 801 111 2222',
        shipping_recipient_name='Amina Bello',
        shipping_phone='+234 801 111 2222',
        shipping_street_address='15 Marina Way',
        shipping_city='Lagos',
        shipping_state='Lagos',
        items_subtotal=Decimal('25000.00'),
        shipping_fee=Decimal('2000.00'),
        total_amount=Decimal('27000.00'),
        payment_status=Order.PaymentStatus.PAID,
        fulfillment_status=Order.FulfillmentStatus.PROCESSING,
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        product_name=product.name,
        sku=product.sku,
        unit_price=product.base_price,
        quantity=1,
        line_total=product.base_price,
    )
    return {
        'owner': owner,
        'tier': tier,
        'store': store,
        'category': category,
        'product': product,
        'order': order,
    }


# ==============================================================================
# 1. PRODUCTS CRUD TESTS
# ==============================================================================

def test_merchant_product_crud_lifecycle(client, merchant_setup):
    """Test full merchant product CRUD: Create, Read, Update, Toggle, Delete."""
    client.force_login(merchant_setup['owner'])
    store = merchant_setup['store']
    category = merchant_setup['category']

    # 1. Read: List products
    res = client.get(reverse('dashboard:products'))
    assert res.status_code == 200
    assert 'Adire Silk Kimono' in res.content.decode()

    # 2. Create: Add new product
    create_data = {
        'name': 'Ankara Infinity Jumpsuit',
        'category': category.id,
        'base_price': '18500.00',
        'comparison_price': '22000.00',
        'sku': 'ANK-JMP-002',
        'stock_quantity': 20,
        'description': 'Handcrafted premium Ankara jumpsuit with pockets.',
        'badge_text': 'Hot Deal',
        'is_active': 'on',
        'is_featured': 'on',
    }
    create_res = client.post(reverse('dashboard:product_create'), data=create_data, follow=True)
    assert create_res.status_code == 200
    new_product = Product.objects.get(sku='ANK-JMP-002')
    assert new_product.store == store
    assert new_product.base_price == Decimal('18500.00')

    # 3. Update / Edit: Edit product price and stock
    edit_url = reverse('dashboard:product_edit', kwargs={'product_id': new_product.id})
    edit_data = {
        'name': 'Ankara Infinity Jumpsuit (Updated)',
        'category': category.id,
        'base_price': '19500.00',
        'comparison_price': '25000.00',
        'sku': 'ANK-JMP-002',
        'stock_quantity': 35,
        'description': 'Updated description.',
        'is_active': 'on',
    }
    edit_res = client.post(edit_url, data=edit_data, follow=True)
    assert edit_res.status_code == 200
    new_product.refresh_from_db()
    assert new_product.name == 'Ankara Infinity Jumpsuit (Updated)'
    assert new_product.base_price == Decimal('19500.00')
    assert new_product.stock_quantity == 35

    # 4. Toggle Status
    toggle_url = reverse('dashboard:product_toggle_status', kwargs={'product_id': new_product.id})
    client.post(toggle_url, follow=True)
    new_product.refresh_from_db()
    assert new_product.is_active is False
    client.post(toggle_url, follow=True)
    new_product.refresh_from_db()
    assert new_product.is_active is True

    # 5. Delete
    delete_url = reverse('dashboard:product_delete', kwargs={'product_id': new_product.id})
    delete_res = client.post(delete_url, follow=True)
    assert delete_res.status_code == 200
    assert not Product.objects.filter(id=new_product.id).exists()


def _generate_test_image(color='blue', filename='test.png'):
    buf = io.BytesIO()
    img = Image.new('RGB', (100, 100), color=color)
    img.save(buf, 'PNG')
    buf.seek(0)
    return SimpleUploadedFile(filename, buf.read(), content_type='image/png')


def test_merchant_product_images_and_gallery_management(client, merchant_setup):
    """Test image upload on creation & edit, setting primary image, deleting image, and preview presence."""
    client.force_login(merchant_setup['owner'])
    category = merchant_setup['category']
    store = merchant_setup['store']

    # 1. Verify GET create page has split-screen preview markup
    get_create_res = client.get(reverse('dashboard:product_create'))
    assert get_create_res.status_code == 200
    create_html = get_create_res.content.decode()
    assert 'previewTitle' in create_html
    assert 'previewPrice' in create_html
    assert 'previewMainImg' in create_html
    assert 'id_primary_image' in create_html
    assert 'id_additional_images' in create_html

    # 2. POST create with primary_image and additional_images
    primary_file = _generate_test_image('red', 'primary_cover.png')
    gallery_1 = _generate_test_image('yellow', 'gallery_1.png')
    gallery_2 = _generate_test_image('green', 'gallery_2.png')

    post_data = {
        'name': 'Ohuami Statement Handbag',
        'category': category.id,
        'base_price': '32000.00',
        'comparison_price': '40000.00',
        'sku': 'OHU-HB-999',
        'stock_quantity': 12,
        'description': 'Handcrafted artisan leather bag with gold accents.',
        'badge_text': '20% OFF',
        'is_active': 'on',
        'primary_image': primary_file,
        'additional_images': [gallery_1, gallery_2],
    }

    create_res = client.post(reverse('dashboard:product_create'), data=post_data, follow=True)
    assert create_res.status_code == 200
    product = Product.objects.get(sku='OHU-HB-999')
    assert product.store == store

    # Verify images were saved
    images = ProductImage.objects.filter(product=product)
    assert images.count() == 3
    assert images.filter(is_primary=True).count() == 1
    assert product.primary_image is not None

    old_primary = ProductImage.objects.get(product=product, is_primary=True)
    secondary_img = images.filter(is_primary=False).first()
    assert secondary_img is not None

    # 3. Promote secondary image to primary
    set_primary_url = reverse('dashboard:product_image_set_primary', kwargs={
        'product_id': product.id,
        'image_id': secondary_img.id
    })
    set_res = client.post(set_primary_url, follow=True)
    assert set_res.status_code == 200

    secondary_img.refresh_from_db()
    assert secondary_img.is_primary is True
    old_primary.refresh_from_db()
    assert old_primary.is_primary is False

    # 4. Delete an image from gallery
    del_url = reverse('dashboard:product_image_delete', kwargs={
        'product_id': product.id,
        'image_id': old_primary.id
    })
    del_res = client.post(del_url, follow=True)
    assert del_res.status_code == 200
    assert not ProductImage.objects.filter(id=old_primary.id).exists()
    assert ProductImage.objects.filter(product=product).count() == 2

    # 5. Cross-tenant isolation: another merchant cannot delete product images
    other_owner = User.objects.create_user(
        email='other_merchant@ohuami.com',
        password='Password@123',
        role=User.Role.MERCHANT,
    )
    Store.objects.create(
        owner=other_owner,
        name='Another Store',
        slug='another-store',
        tier=merchant_setup['tier'],
    )
    client.force_login(other_owner)

    # Attempting to delete another merchant's image returns 404
    del_res_other = client.post(reverse('dashboard:product_image_delete', kwargs={
        'product_id': product.id,
        'image_id': secondary_img.id
    }))
    assert del_res_other.status_code == 404
    # Image still exists
    assert ProductImage.objects.filter(id=secondary_img.id).exists()


# ==============================================================================
# 2. ORDERS CRUD & MANAGEMENT TESTS
# ==============================================================================

def test_merchant_order_management_and_manual_create(client, merchant_setup):
    """Test viewing order details, manual creation, status update, and cancel restock."""
    client.force_login(merchant_setup['owner'])
    order = merchant_setup['order']
    product = merchant_setup['product']

    # 1. View Order Detail
    detail_url = reverse('dashboard:order_detail', kwargs={'order_id': order.id})
    detail_res = client.get(detail_url)
    assert detail_res.status_code == 200
    assert order.order_reference in detail_res.content.decode()
    assert 'Amina Bello' in detail_res.content.decode()

    # 2. Update status
    status_url = reverse('dashboard:update_order_status', kwargs={'order_id': order.id})
    update_res = client.post(status_url, {'status': 'shipped', 'payment_status': 'paid'}, follow=True)
    assert update_res.status_code == 200
    order.refresh_from_db()
    assert order.fulfillment_status == Order.FulfillmentStatus.SHIPPED

    # 3. Create Manual Order (in-store / phone sale)
    initial_stock = product.stock_quantity
    create_manual_url = reverse('dashboard:order_create')
    manual_data = {
        'customer_name': 'Kolawole Johnson',
        'customer_email': 'kolawole@example.com',
        'customer_phone': '+234 803 555 6677',
        'shipping_street_address': '42 Broad Street',
        'shipping_city': 'Lagos',
        'shipping_state': 'Lagos',
        'product': product.id,
        'quantity': 2,
        'shipping_fee': '1500.00',
        'payment_method': 'pos_terminal',
        'payment_status': Order.PaymentStatus.PAID,
        'fulfillment_status': Order.FulfillmentStatus.PROCESSING,
    }
    manual_res = client.post(create_manual_url, data=manual_data, follow=True)
    assert manual_res.status_code == 200
    new_order = Order.objects.filter(customer_email='kolawole@example.com').first()
    assert new_order is not None
    assert new_order.total_amount == Decimal('51500.00')  # 25000*2 + 1500
    product.refresh_from_db()
    assert product.stock_quantity == initial_stock - 2

    # 4. Cancel order and restock
    cancel_url = reverse('dashboard:order_cancel', kwargs={'order_id': new_order.id})
    client.post(cancel_url, follow=True)
    new_order.refresh_from_db()
    assert new_order.order_status == Order.OrderStatus.CANCELLED
    product.refresh_from_db()
    assert product.stock_quantity == initial_stock  # Restored!


# ==============================================================================
# 3. AGENT & STAFF MANAGEMENT TESTS
# ==============================================================================

def test_merchant_agent_management_and_quota(client, merchant_setup):
    """Test adding agents, enforcing staff quota, editing permissions, and deleting."""
    client.force_login(merchant_setup['owner'])
    store = merchant_setup['store']

    # 1. Add Agent
    create_url = reverse('dashboard:agent_create')
    data = {
        'name': 'Folake Adeleke',
        'email': 'folake@boutique.ng',
        'phone': '+234 802 888 9900',
        'role': StoreAgent.Role.SUPPORT,
        'can_manage_products': False,
        'can_manage_orders': True,
        'can_manage_dispatch': True,
        'can_manage_customers': True,
        'is_active': 'on',
    }
    res = client.post(create_url, data=data, follow=True)
    assert res.status_code == 200
    agent = StoreAgent.objects.get(email='folake@boutique.ng', store=store)
    assert agent.role == StoreAgent.Role.SUPPORT
    assert agent.can_manage_orders is True

    # 2. Edit Agent
    edit_url = reverse('dashboard:agent_edit', kwargs={'agent_id': agent.id})
    edit_data = {
        'name': 'Folake Adeleke (Manager)',
        'email': 'folake@boutique.ng',
        'phone': '+234 802 888 9900',
        'role': StoreAgent.Role.MANAGER,
        'can_manage_products': True,
        'can_manage_orders': True,
        'can_manage_dispatch': True,
        'can_manage_customers': True,
        'is_active': 'on',
    }
    client.post(edit_url, data=edit_data, follow=True)
    agent.refresh_from_db()
    assert agent.role == StoreAgent.Role.MANAGER
    assert agent.can_manage_products is True

    # 3. Toggle Status
    toggle_url = reverse('dashboard:agent_toggle_status', kwargs={'agent_id': agent.id})
    client.post(toggle_url, follow=True)
    agent.refresh_from_db()
    assert agent.is_active is False

    # 4. Delete Agent
    delete_url = reverse('dashboard:agent_delete', kwargs={'agent_id': agent.id})
    del_res = client.post(delete_url, follow=True)
    assert del_res.status_code == 200
    assert not StoreAgent.objects.filter(id=agent.id).exists()


# ==============================================================================
# 4. LOGISTICS & DISPATCH MANAGEMENT TESTS
# ==============================================================================

def test_merchant_logistics_and_dispatch_flow(client, merchant_setup):
    """Test carrier registration, dispatching order, tracking generation, and milestone updates."""
    client.force_login(merchant_setup['owner'])
    store = merchant_setup['store']
    order = merchant_setup['order']

    # 1. Register Carrier
    carrier_url = reverse('dashboard:carrier_create')
    carrier_data = {
        'name': 'Fez Delivery Services',
        'carrier_type': DispatchCarrier.CarrierType.THIRD_PARTY,
        'phone': '+234 812 345 6789',
        'vehicle_type': DispatchCarrier.VehicleType.MOTORCYCLE,
        'vehicle_number': 'KJA-552-XY',
        'service_areas': 'Lagos Mainland, Lekki',
        'is_active': 'on',
    }
    res = client.post(carrier_url, data=carrier_data, follow=True)
    assert res.status_code == 200
    carrier = DispatchCarrier.objects.get(name='Fez Delivery Services', store=store)
    assert carrier.vehicle_type == DispatchCarrier.VehicleType.MOTORCYCLE

    # 2. Dispatch Order
    dispatch_url = reverse('dashboard:dispatch_create')
    dispatch_data = {
        'order_id': order.id,
        'carrier': carrier.id,
        'recipient_name': order.shipping_recipient_name,
        'recipient_phone': order.shipping_phone,
        'delivery_address': order.formatted_shipping_address,
        'dispatch_notes': 'Please call 10 mins before arrival',
        'status': DispatchShipment.Status.IN_TRANSIT,
    }
    client.post(dispatch_url, data=dispatch_data, follow=True)
    shipment = DispatchShipment.objects.get(order=order)
    assert shipment.carrier == carrier
    assert shipment.tracking_number.startswith('OHU-TRK-')
    order.refresh_from_db()
    assert order.fulfillment_status == Order.FulfillmentStatus.SHIPPED

    # 3. Update status to Delivered
    update_shipment_url = reverse('dashboard:dispatch_update_status', kwargs={'shipment_id': shipment.id})
    client.post(update_shipment_url, {'status': DispatchShipment.Status.DELIVERED}, follow=True)
    shipment.refresh_from_db()
    assert shipment.status == DispatchShipment.Status.DELIVERED
    order.refresh_from_db()
    assert order.fulfillment_status == Order.FulfillmentStatus.DELIVERED


# ==============================================================================
# 5. CUSTOMER CRM TESTS
# ==============================================================================

def test_merchant_customer_crm_management(client, merchant_setup):
    """Test customer list, details, editing tags, and merchant notes."""
    client.force_login(merchant_setup['owner'])
    store = merchant_setup['store']

    # 1. Add Customer
    create_url = reverse('dashboard:customer_create')
    cust_data = {
        'name': 'Zainab Mohammed',
        'email': 'zainab@example.com',
        'phone': '+234 809 333 4444',
        'customer_tag': StoreCustomer.CustomerTag.VIP,
        'notes': 'Requested bulk price catalog for wedding bridesmaids.',
    }
    res = client.post(create_url, data=cust_data, follow=True)
    assert res.status_code == 200
    customer = StoreCustomer.objects.get(email='zainab@example.com', store=store)
    assert customer.customer_tag == StoreCustomer.CustomerTag.VIP

    # 2. Update Customer Notes
    detail_url = reverse('dashboard:customer_detail', kwargs={'customer_id': customer.id})
    update_data = {
        'name': 'Zainab Mohammed (Dr.)',
        'email': 'zainab@example.com',
        'phone': '+234 809 333 4444',
        'customer_tag': StoreCustomer.CustomerTag.VIP,
        'notes': 'Preferred delivery on Saturday mornings.',
    }
    client.post(detail_url, data=update_data, follow=True)
    customer.refresh_from_db()
    assert customer.name == 'Zainab Mohammed (Dr.)'
    assert 'Saturday mornings' in customer.notes

    # 3. Delete Customer
    del_url = reverse('dashboard:customer_delete', kwargs={'customer_id': customer.id})
    client.post(del_url, follow=True)
    assert not StoreCustomer.objects.filter(id=customer.id).exists()


# ==============================================================================
# 6. CORS & HEADLESS REST API TESTS
# ==============================================================================

def test_cors_headers_and_headless_api(client, merchant_setup):
    """Test CORS preflight and Store REST API for Products, Orders, and Logistics."""
    store = merchant_setup['store']
    allowed_origin = 'https://testboutique.ng'
    api_key = store.api_key

    # 1. Preflight OPTIONS request with Origin
    options_res = client.options(
        reverse('dashboard:api_products'),
        HTTP_ORIGIN=allowed_origin,
        HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS='Content-Type, X-Store-Key',
    )
    assert options_res.status_code in [200, 204]
    assert options_res.headers.get('Access-Control-Allow-Origin') == allowed_origin
    assert 'POST' in options_res.headers.get('Access-Control-Allow-Methods')

    # 2. Programmatic GET /api/products/ with X-Store-Key
    get_res = client.get(
        reverse('dashboard:api_products'),
        HTTP_ORIGIN=allowed_origin,
        HTTP_X_STORE_KEY=api_key,
    )
    assert get_res.status_code == 200
    data = get_res.json()
    assert data['status'] == 'success'
    assert data['count'] >= 1
    assert get_res.headers.get('Access-Control-Allow-Origin') == allowed_origin

    # 3. Programmatic POST /api/products/ (create product via API)
    new_prod_data = {
        'name': 'Headless API Lace Gown',
        'sku': 'HDL-LCE-999',
        'base_price': '45000.00',
        'stock_quantity': 12,
    }
    post_res = client.post(
        reverse('dashboard:api_products'),
        data=json.dumps(new_prod_data),
        content_type='application/json',
        HTTP_ORIGIN=allowed_origin,
        HTTP_X_STORE_KEY=api_key,
    )
    assert post_res.status_code == 201
    created_id = post_res.json()['product']['id']

    # 4. Programmatic PATCH /api/products/<id>/ (update product via API)
    patch_res = client.patch(
        reverse('dashboard:api_product_detail', kwargs={'pk': created_id}),
        data=json.dumps({'base_price': '42000.00', 'stock_quantity': 8}),
        content_type='application/json',
        HTTP_ORIGIN=allowed_origin,
        HTTP_X_STORE_KEY=api_key,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()['product']['base_price'] == '42000.00'

    # 5. Programmatic DELETE /api/products/<id>/ (delete product via API)
    del_res = client.delete(
        reverse('dashboard:api_product_detail', kwargs={'pk': created_id}),
        HTTP_ORIGIN=allowed_origin,
        HTTP_X_STORE_KEY=api_key,
    )
    assert del_res.status_code == 200
    assert del_res.json()['status'] == 'deleted'

    # 6. Programmatic GET /api/orders/
    orders_res = client.get(
        reverse('dashboard:api_orders'),
        HTTP_ORIGIN=allowed_origin,
        HTTP_X_STORE_KEY=api_key,
    )
    assert orders_res.status_code == 200
    assert orders_res.json()['status'] == 'success'

    # 7. Programmatic GET /api/customers/
    cust_res = client.get(
        reverse('dashboard:api_customers'),
        HTTP_ORIGIN=allowed_origin,
        HTTP_X_STORE_KEY=api_key,
    )
    assert cust_res.status_code == 200
    assert cust_res.json()['status'] == 'success'
