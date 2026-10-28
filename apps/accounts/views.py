from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User
from apps.orders.models import Order
from apps.cart.services import CartService


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    next_url = request.GET.get('next') or request.POST.get('next') or 'accounts:profile'
    error = None

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            old_session_key = request.session.session_key
            login(request, user)
            # Merge session cart into user cart if guest cart existed
            if old_session_key:
                from apps.cart.models import Cart
                session_cart = Cart.objects.filter(session_key=old_session_key, user__isnull=True).first()
                if session_cart:
                    user_cart, _ = Cart.objects.get_or_create(user=user)
                    CartService.merge_carts(session_cart, user_cart)
            return redirect(next_url)
        else:
            error = "Invalid email address or password. Please try again."

    return render(request, 'accounts/login.html', {'error': error, 'next': next_url})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')

        if User.objects.filter(email=email).exists():
            error = "An account with this email address already exists."
        elif len(password) < 8:
            error = "Password must be at least 8 characters long."
        else:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            login(request, user)
            CartService.get_or_create_cart(request)
            return redirect('accounts:profile')

    return render(request, 'accounts/register.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('core:home')


@login_required
def profile_view(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')[:5]
    return render(request, 'accounts/profile.html', {'orders': orders})
