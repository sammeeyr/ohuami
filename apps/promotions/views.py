from django.shortcuts import render
from apps.catalog.models import Product
from .models import Coupon, Campaign


def flash_sale_view(request):
    flash_products = Product.objects.filter(is_active=True, is_flash_sale=True)
    campaign = Campaign.objects.filter(is_active=True).first()
    return render(request, 'catalog/list.html', {
        'products': flash_products,
        'title': 'Flash Sale Deals',
        'current_category': None,
        'campaign': campaign,
    })


def coupons_view(request):
    coupons = Coupon.objects.filter(is_active=True)
    return render(request, 'promotions/coupons.html', {'coupons': coupons})
