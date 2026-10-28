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


def order_history(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(customer=request.user).prefetch_related('items')
    else:
        # Check session email or recent order refs
        orders = Order.objects.none()

    return render(request, 'orders/history.html', {'orders': orders})
