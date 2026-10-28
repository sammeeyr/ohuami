import json
from decimal import Decimal
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.adapters.factory import get_payment_adapter


def payment_callback(request):
    reference = request.GET.get('reference') or request.GET.get('trxref')
    if not reference:
        return redirect('core:home')

    order_ref = reference.replace('SANDBOX-', '')
    order = Order.objects.filter(order_reference=order_ref).first()
    if not order:
        return redirect('core:home')

    adapter = get_payment_adapter(order.payment_method)
    verify_res = adapter.verify_payment(reference)

    if verify_res.get('success'):
        order.payment_status = Order.PaymentStatus.PAID
        order.paid_at = timezone.now()
        order.save()

        payment = Payment.objects.filter(order=order).first()
        if payment:
            payment.status = Payment.Status.SUCCESS
            payment.gateway_reference = str(verify_res.get('gateway_reference', ''))
            payment.channel = verify_res.get('channel', '')
            payment.raw_response = verify_res.get('raw', {})
            payment.save()

    return redirect('orders:confirmation', order_ref=order.order_reference)


@csrf_exempt
@require_POST
def paystack_webhook(request):
    signature = request.headers.get('x-paystack-signature') or request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
    payload = request.body
    adapter = get_payment_adapter('paystack')

    if not adapter.verify_webhook_signature(payload, signature):
        return HttpResponse("Invalid signature", status=400)

    try:
        event_data = json.loads(payload.decode('utf-8'))
        event_type = event_data.get('event')

        if event_type == 'charge.success':
            data = event_data.get('data', {})
            reference = data.get('reference')
            amount_kobo = data.get('amount')
            currency = data.get('currency', 'NGN')

            order = Order.objects.filter(order_reference=reference).first()
            if order:
                expected_kobo = int(order.total_amount * 100)
                if amount_kobo == expected_kobo and currency == order.currency:
                    order.payment_status = Order.PaymentStatus.PAID
                    order.paid_at = timezone.now()
                    order.save()

                    payment, _ = Payment.objects.get_or_create(
                        order=order,
                        reference=reference,
                        defaults={
                            'amount': order.total_amount,
                            'currency': currency,
                            'gateway': 'paystack'
                        }
                    )
                    payment.status = Payment.Status.SUCCESS
                    payment.gateway_reference = str(data.get('id', ''))
                    payment.raw_response = data
                    payment.channel = data.get('channel', '')
                    payment.save()

        return HttpResponse("Webhook processed successfully", status=200)
    except Exception as e:
        return HttpResponse(f"Error processing webhook: {str(e)}", status=500)
