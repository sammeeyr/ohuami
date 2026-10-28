from .paystack import PaystackPaymentAdapter
from .sandbox import SandboxPaymentAdapter


def get_payment_adapter(gateway_name='paystack'):
    gateway_name = (gateway_name or 'paystack').lower()
    if gateway_name == 'sandbox':
        return SandboxPaymentAdapter()
    elif gateway_name == 'paystack':
        return PaystackPaymentAdapter()
    # Default fallback
    return PaystackPaymentAdapter()
