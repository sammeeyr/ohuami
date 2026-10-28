from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from apps.catalog.models import Product, Category
from apps.promotions.models import Campaign


@ensure_csrf_cookie
def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related('category')[:8]
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'core/marketing_home.html', context)
