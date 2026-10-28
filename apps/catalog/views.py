from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Store, Product, Category, Brand


@ensure_csrf_cookie
def storefront(request, store_slug=None):
    if not store_slug:
        store_slug = 'sunshine-fashion'
    
    store = Store.objects.filter(slug=store_slug, is_active=True).first()
    if not store:
        store = Store.objects.first()

    # Scope products strictly to current store tenant
    if store:
        featured_products = Product.objects.filter(store=store, is_active=True).select_related('category', 'brand')
    else:
        featured_products = Product.objects.filter(is_active=True).select_related('category', 'brand')

    # Circular categories
    categories = Category.objects.filter(is_active=True, slug__in=['women', 'men', 'bags', 'shoes', 'accessories', 'beauty']).order_by('display_order')
    if not categories.exists():
        categories = Category.objects.filter(is_active=True)[:6]

    context = {
        'store': store,
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'catalog/storefront.html', context)


@ensure_csrf_cookie
def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category', 'brand')
    categories = Category.objects.filter(is_active=True, parent__isnull=True)
    
    sort = request.GET.get('sort', 'featured')
    if sort == 'latest':
        products = products.order_by('-created_at')
    elif sort == 'price_asc':
        products = products.order_by('base_price')
    elif sort == 'price_desc':
        products = products.order_by('-base_price')
    elif sort == 'popular':
        products = products.order_by('-is_trending', '-is_featured', '-created_at')
    else:
        products = products.order_by('-is_featured', '-created_at')

    filter_type = request.GET.get('filter')
    if filter_type == 'flash':
        products = products.filter(is_flash_sale=True)

    context = {
        'products': products,
        'categories': categories,
        'current_category': None,
        'sort': sort,
    }
    return render(request, 'catalog/list.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(is_active=True, category=category).select_related('category', 'brand')
    categories = Category.objects.filter(is_active=True, parent__isnull=True)

    sort = request.GET.get('sort', 'featured')
    if sort == 'price_asc':
        products = products.order_by('base_price')
    elif sort == 'price_desc':
        products = products.order_by('-base_price')
    else:
        products = products.order_by('-is_featured', '-created_at')

    context = {
        'products': products,
        'categories': categories,
        'current_category': category,
        'sort': sort,
    }
    return render(request, 'catalog/list.html', context)


@ensure_csrf_cookie
def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related('images', 'variants__attribute_values', 'reviews'),
        slug=slug, 
        is_active=True
    )
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'catalog/product_detail.html', context)


def search(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.filter(is_active=True).select_related('category', 'brand')
    categories = Category.objects.filter(is_active=True, parent__isnull=True)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(sku__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'current_category': None,
        'sort': 'featured',
    }
    return render(request, 'catalog/list.html', context)
