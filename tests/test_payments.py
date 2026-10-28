import hmac
import hashlib
import json
import pytest
from decimal import Decimal
from django.urls import reverse
from apps.payments.adapters.paystack import PaystackPaymentAdapter
from apps.payments.adapters.sandbox import SandboxPaymentAdapter
from apps.orders.models import Order


@pytest.mark.django_db
def test_sandbox_payment_adapter():
    adapter = SandboxPaymentAdapter()
    res = adapter.verify_payment("SANDBOX-REF-001")
    assert res['success'] is True
    assert res['status'] == 'success'


def test_paystack_webhook_signature_verification():
    secret = "sk_test_mock_secret_key_cubetech"
    adapter = PaystackPaymentAdapter(webhook_secret=secret)

    payload = b'{"event":"charge.success","data":{"reference":"CT-20261028-TEST"}}'
    valid_signature = hmac.new(secret.encode('utf-8'), payload, hashlib.sha512).hexdigest()

    assert adapter.verify_webhook_signature(payload, valid_signature) is True
    assert adapter.verify_webhook_signature(payload, "invalid_tampered_signature") is False


@pytest.mark.django_db
def test_paystack_webhook_endpoint(client):
    from django.conf import settings
    secret = getattr(settings, 'PAYSTACK_WEBHOOK_SECRET')
    adapter = PaystackPaymentAdapter(webhook_secret=secret)

    order = Order.objects.create(
        customer_email="payer@example.com",
        customer_phone="08012345678",
        customer_name="Payer One",
        shipping_recipient_name="Payer One",
        shipping_phone="08012345678",
        shipping_street_address="Street 10",
        shipping_city="Abuja",
        shipping_state="FCT Abuja",
        items_subtotal=Decimal("50000.00"),
        total_amount=Decimal("50000.00"),
        currency="NGN",
        payment_method="paystack"
    )

    payload_dict = {
        "event": "charge.success",
        "data": {
            "reference": order.order_reference,
            "amount": 5000000, # 50,000 NGN in kobo
            "currency": "NGN",
            "id": "mock_paystack_id_1234",
            "channel": "card"
        }
    }
    payload_bytes = json.dumps(payload_dict).encode('utf-8')
    sig = hmac.new(secret.encode('utf-8'), payload_bytes, hashlib.sha512).hexdigest()

    response = client.post(
        reverse('payments:paystack_webhook'),
        data=payload_bytes,
        content_type='application/json',
        HTTP_X_PAYSTACK_SIGNATURE=sig
    )

    assert response.status_code == 200
    order.refresh_from_db()
    assert order.payment_status == Order.PaymentStatus.PAID
