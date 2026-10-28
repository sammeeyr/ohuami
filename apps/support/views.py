import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ChatMessage, SupportEnquiry


@require_POST
def api_chat(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        if not message:
            return JsonResponse({'reply': 'Please type a valid message.'})

        session_id = request.session.session_key or 'anonymous_session'
        ChatMessage.objects.create(session_id=session_id, sender='customer', text=message)

        # Smart automated assistance replies
        msg_lower = message.lower()
        if any(w in msg_lower for w in ['track', 'order', 'status']):
            reply = "You can track your order in the 'Account > My Orders' section or check your email receipt for your order reference number (e.g., CT-20261028-XXXX)."
        elif any(w in msg_lower for w in ['pay', 'paystack', 'transfer', 'card']):
            reply = "We accept all Nigerian bank debit cards (Mastercard, Visa, Verve), Direct Bank Transfers, and USSD via our secured Paystack integration."
        elif any(w in msg_lower for w in ['delivery', 'ship', 'lagos', 'abuja']):
            reply = "We deliver across Nigeria! Orders within Abuja & Lagos arrive within 24 hours. Nationwide delivery takes 2 to 4 business days. Free delivery applies on orders over ₦50,000."
        elif any(w in msg_lower for w in ['warranty', 'return', 'guarantee']):
            reply = "All Cube Tech products come with a minimum 12-month official manufacturer warranty and a 7-day hassle-free replacement guarantee."
        else:
            reply = "Thank you for reaching out to Cube Tech Enterprises! A customer care specialist has been alerted and will assist you shortly. You can also call us directly at +234 800 2823 8324."

        ChatMessage.objects.create(session_id=session_id, sender='agent', text=reply)
        return JsonResponse({'reply': reply})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
