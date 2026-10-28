from abc import ABC, abstractmethod


class PaymentAdapter(ABC):
    @abstractmethod
    def initialize_payment(self, order, callback_url, customer_email=None):
        """
        Initializes a payment transaction on the gateway.
        Returns a dict: {'success': bool, 'authorization_url': str, 'reference': str, 'error': str}
        """
        pass

    @abstractmethod
    def verify_payment(self, reference):
        """
        Verifies transaction status directly with gateway API.
        Returns a dict: {'success': bool, 'amount': Decimal, 'currency': str, 'status': str, 'raw': dict}
        """
        pass

    @abstractmethod
    def verify_webhook_signature(self, payload, signature):
        """
        Validates webhook HMAC signature against secret key.
        Returns bool
        """
        pass
