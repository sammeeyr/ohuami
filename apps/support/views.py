import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.core.models import StoreSetting
from .models import ChatMessage, SupportEnquiry
from .forms import SupportEnquiryForm


def contact_view(request):
    """Customer care and support enquiry ticketing page."""
    submitted_ticket = None
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'name': request.user.get_full_name() or request.user.email.split('@')[0],
            'email': request.user.email,
            'phone': request.user.phone,
        }

    if request.method == 'POST':
        form = SupportEnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            if request.user.is_authenticated:
                enquiry.user = request.user
            enquiry.save()
            submitted_ticket = enquiry.ticket_number
            messages.success(request, f"Your support ticket #{enquiry.ticket_number} has been created! Our team will contact you shortly.")
            form = SupportEnquiryForm(initial=initial_data)
        else:
            messages.error(request, "Please check the form inputs and try again.")
    else:
        form = SupportEnquiryForm(initial=initial_data)

    settings = StoreSetting.get_settings()

    faqs = [
        {
            'question': "How fast is delivery within Nigeria?",
            'answer': "Orders within Abuja and Lagos are delivered within 24 hours. For all other states across Nigeria, standard delivery takes 2 to 4 business days. Express same-day shipping is also available in select locations."
        },
        {
            'question': "What payment options are supported?",
            'answer': "We accept Nigerian bank debit cards (Mastercard, Visa, Verve), Direct Bank Transfers, USSD quick checkout, and Pay on Delivery for verified addresses via our Paystack gateway."
        },
        {
            'question': "What is the return and refund policy?",
            'answer': "We offer a 7-day hassle-free return window for items in original, undamaged packaging. Refunds are processed back to your original payment method within 3 to 5 business days."
        },
        {
            'question': "How do I become a merchant on OHUAMI?",
            'answer': "You can sign up directly as a merchant from our homepage or contact our merchant onboarding team at merchant-support@ohuami.com to configure your store tier, BVN verification, and custom domain."
        },
        {
            'question': "How can I track my order?",
            'answer': "Navigate to Account > My Orders to view live timeline tracking (Placed → Payment Verified → Processing → Dispatched → Delivered)."
        }
    ]

    context = {
        'form': form,
        'submitted_ticket': submitted_ticket,
        'store_setting': settings,
        'faqs': faqs,
    }
    return render(request, 'support/contact.html', context)


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
