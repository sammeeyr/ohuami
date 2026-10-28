import uuid
from decimal import Decimal
from django.urls import reverse
from .base import PaymentAdapter


class SandboxPaymentAdapter(PaymentAdapter):
    """
    Sandbox / Development Mode Payment Adapter.
    Instantly verifies and simulates completed transactions safely.
    """
    def initialize_payment(self, order, callback_url, customer_email=None):
        reference = f"SANDBOX-{order.order_reference}"
        success_url = f"{callback_url}?reference={reference}&status=success"
        return {
            "success": True,
            "authorization_url": success_url,
            "reference": reference,
            "access_code": f"sandbox_code_{uuid.uuid4().hex[:6]}"
        }

    def verify_payment(self, reference):
        return {
            "success": True,
            "status": "success",
            "amount": Decimal('0.00'), # Checked against order total in service
            "currency": "NGN",
            "gateway_reference": f"mock_tx_{uuid.uuid4().hex[:8]}",
            "channel": "sandbox_card",
            "raw": {"status": "success", "message": "Sandbox payment approved"}
        }

    def verify_webhook_signature(self, payload_bytes, signature):
        return True
