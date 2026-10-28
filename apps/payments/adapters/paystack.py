import hmac
import hashlib
import requests
from decimal import Decimal
from django.conf import settings
from .base import PaymentAdapter


class PaystackPaymentAdapter(PaymentAdapter):
    BASE_URL = "https://api.paystack.co"

    def __init__(self, secret_key=None, public_key=None, webhook_secret=None):
        self.secret_key = secret_key or getattr(settings, 'PAYSTACK_SECRET_KEY', '')
        self.public_key = public_key or getattr(settings, 'PAYSTACK_PUBLIC_KEY', '')
        self.webhook_secret = webhook_secret or getattr(settings, 'PAYSTACK_WEBHOOK_SECRET', self.secret_key)

    def initialize_payment(self, order, callback_url, customer_email=None):
        # Convert total amount to kobo (integer)
        amount_kobo = int(order.total_amount * 100)
        email = customer_email or order.customer_email

        payload = {
            "email": email,
            "amount": amount_kobo,
            "reference": order.order_reference,
            "callback_url": callback_url,
            "currency": order.currency or "NGN",
            "metadata": {
                "order_id": order.id,
                "order_reference": order.order_reference,
                "customer_name": order.customer_name,
            }
        }

        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(f"{self.BASE_URL}/transaction/initialize", json=payload, headers=headers, timeout=12)
            res_data = response.json()
            if response.status_code == 200 and res_data.get("status"):
                return {
                    "success": True,
                    "authorization_url": res_data["data"]["authorization_url"],
                    "reference": res_data["data"]["reference"],
                    "access_code": res_data["data"]["access_code"]
                }
            else:
                return {
                    "success": False,
                    "error": res_data.get("message", "Payment initialization failed on Paystack")
                }
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def verify_payment(self, reference):
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(f"{self.BASE_URL}/transaction/verify/{reference}", headers=headers, timeout=12)
            res_data = response.json()
            if response.status_code == 200 and res_data.get("status"):
                data = res_data["data"]
                status = data.get("status") # 'success', 'failed', 'abandoned'
                amount = Decimal(str(data.get("amount", 0))) / Decimal('100.00')
                currency = data.get("currency", "NGN")

                return {
                    "success": status == "success",
                    "status": status,
                    "amount": amount,
                    "currency": currency,
                    "gateway_reference": data.get("id"),
                    "channel": data.get("channel"),
                    "raw": data
                }
            return {"success": False, "status": "failed", "error": res_data.get("message", "Verification failed")}
        except Exception as e:
            return {"success": False, "status": "error", "error": str(e)}

    def verify_webhook_signature(self, payload_bytes, signature):
        if not signature or not self.webhook_secret:
            return False
        computed = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha512
        ).hexdigest()
        return hmac.compare_digest(computed, signature)
