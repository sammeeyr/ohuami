import pytest
from decimal import Decimal
from django.urls import reverse
from apps.accounts.models import User
from apps.orders.models import Order


@pytest.mark.django_db
def test_cross_customer_order_isolation(client):
    user_a = User.objects.create_user(email="alice@example.com", password="Password123!")
    user_b = User.objects.create_user(email="bob@example.com", password="Password123!")

    # Order belonging to User A
    order_a = Order.objects.create(
        customer=user_a,
        customer_email="alice@example.com",
        customer_phone="08011111111",
        customer_name="Alice",
        shipping_recipient_name="Alice",
        shipping_phone="08011111111",
        shipping_street_address="Alice Ave",
        shipping_city="Abuja",
        shipping_state="FCT Abuja",
        items_subtotal=Decimal("10000.00"),
        total_amount=Decimal("10000.00")
    )

    # Log in as User B
    client.force_login(user_b)

    # User B attempts to access User A's order confirmation
    response = client.get(reverse('orders:confirmation', kwargs={'order_ref': order_a.order_reference}))
    
    # Should redirect unauthorized user away to home
    assert response.status_code == 302
    assert response.url == reverse('core:home')


@pytest.mark.django_db
def test_password_length_enforcement(client):
    # Attempt registration with short password (less than 8 chars)
    response = client.post(reverse('accounts:register'), {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'shortpass@example.com',
        'phone': '08000000000',
        'password': '123'
    })
    assert response.status_code == 200
    assert "at least 8 characters" in response.content.decode('utf-8')
    assert not User.objects.filter(email='shortpass@example.com').exists()
