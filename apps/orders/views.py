from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order


def order_confirmation(request, order_ref):
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        order_reference=order_ref
    )
    # Check permissions: if order has a customer, only allow that customer or staff (unless anonymous guest)
    if order.customer and request.user.is_authenticated and order.customer != request.user and not request.user.is_staff:
        return redirect('core:home')

    return render(request, 'orders/confirmation.html', {'order': order})


def order_detail(request, order_ref):
    """Detailed order view with tracking timeline and item breakdown."""
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        order_reference=order_ref
    )
    if order.customer and request.user.is_authenticated and order.customer != request.user and not request.user.is_staff:
        return redirect('core:home')

    # Compute timeline progress
    # Statuses: PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED
    status_step = 1
    if order.payment_status == Order.PaymentStatus.PAID:
        status_step = 2
    if order.fulfillment_status == Order.FulfillmentStatus.PROCESSING:
        status_step = 3
    elif order.fulfillment_status == Order.FulfillmentStatus.SHIPPED:
        status_step = 4
    elif order.fulfillment_status == Order.FulfillmentStatus.DELIVERED:
        status_step = 5

    context = {
        'order': order,
        'status_step': status_step,
    }
    return render(request, 'orders/detail.html', context)


def order_history(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(customer=request.user).prefetch_related('items').order_by('-created_at')
    else:
        orders = Order.objects.none()

    return render(request, 'orders/history.html', {'orders': orders})
