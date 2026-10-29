from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import User, Address
from .forms import ProfileUpdateForm, AddressForm, ChangePasswordForm
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
    """Customer account center with addresses, profile details, and orders."""
    user = request.user
    orders = Order.objects.filter(customer=user).order_by('-created_at')[:8]
    addresses = user.addresses.all()

    profile_form = ProfileUpdateForm(instance=user)
    address_form = AddressForm()
    password_form = ChangePasswordForm(user=user)

    context = {
        'orders': orders,
        'addresses': addresses,
        'profile_form': profile_form,
        'address_form': address_form,
        'password_form': password_form,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
@require_POST
def update_profile_view(request):
    form = ProfileUpdateForm(request.POST, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Your profile information has been updated.")
    else:
        messages.error(request, "Failed to update profile. Please verify your entries.")
    return redirect('accounts:profile')


@login_required
@require_POST
def add_address_view(request):
    form = AddressForm(request.POST)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        messages.success(request, "New delivery address saved successfully!")
    else:
        messages.error(request, "Could not save address. Please check all required fields.")
    return redirect('accounts:profile')


@login_required
@require_POST
def delete_address_view(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted.")
    return redirect('accounts:profile')


@login_required
@require_POST
def set_default_address_view(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, f"'{address.recipient_name}' set as your default shipping address.")
    return redirect('accounts:profile')


@login_required
@require_POST
def change_password_view(request):
    form = ChangePasswordForm(user=request.user, data=request.POST)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Your password was successfully updated!")
    else:
        errors = "; ".join([f"{k}: {', '.join(v)}" for k, v in form.errors.items()])
        messages.error(request, f"Password change error: {errors}")
    return redirect('accounts:profile')
