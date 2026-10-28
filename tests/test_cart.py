import json
import pytest
from decimal import Decimal
from django.urls import reverse
from apps.cart.models import Cart
from apps.accounts.models import User


@pytest.mark.django_db
def test_add_and_update_cart(client, sample_product):
    # 1. Add item
    add_res = client.post(
        reverse('cart:api_add'),
        data=json.dumps({'product_id': sample_product.id, 'quantity': 2}),
        content_type='application/json'
    )
    assert add_res.status_code == 200
    data = add_res.json()
    assert data['success'] is True
    assert data['cart_count'] == 2

    # Verify Cart in DB
    cart = Cart.objects.filter(session_key=client.session.session_key).first()
    assert cart is not None
    assert cart.total_items == 2
    assert cart.subtotal == sample_product.base_price * 2

    # 2. Update item quantity
    item = cart.items.first()
    update_res = client.post(
        reverse('cart:api_update'),
        data=json.dumps({'item_id': item.id, 'quantity': 3}),
        content_type='application/json'
    )
    assert update_res.status_code == 200
    assert update_res.json()['cart_count'] == 3

    # 3. Reject quantity exceeding stock
    exceed_res = client.post(
        reverse('cart:api_update'),
        data=json.dumps({'item_id': item.id, 'quantity': 9999}),
        content_type='application/json'
    )
    assert exceed_res.json()['success'] is False

    # 4. Remove item
    remove_res = client.post(
        reverse('cart:api_remove'),
        data=json.dumps({'item_id': item.id}),
        content_type='application/json'
    )
    assert remove_res.status_code == 200
    assert remove_res.json()['cart_count'] == 0


@pytest.mark.django_db
def test_guest_cart_merges_on_login(client, sample_product):
    # Guest adds item
    client.post(
        reverse('cart:api_add'),
        data=json.dumps({'product_id': sample_product.id, 'quantity': 1}),
        content_type='application/json'
    )
    
    user = User.objects.create_user(email="merge_user@example.com", password="Password123!")
    client.post(reverse('accounts:login'), {'email': 'merge_user@example.com', 'password': 'Password123!'})

    # The user's cart now contains the item
    user_cart = Cart.objects.filter(user=user).first()
    assert user_cart is not None
    assert user_cart.total_items == 1
