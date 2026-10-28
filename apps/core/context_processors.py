from django.conf import settings
from apps.catalog.models import Category, Store, MerchantTier
from apps.cart.models import Cart
from apps.wishlist.models import WishlistItem
from apps.core.models import StoreSetting, PlatformService


def global_context(request):
    store_setting = StoreSetting.get_settings()
    
    # Calculate cart count
    cart_count = 0
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        if request.session.session_key:
            cart = Cart.objects.filter(session_key=request.session.session_key).first()
    if cart:
        cart_count = cart.total_items

    # Wishlist count
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = WishlistItem.objects.filter(user=request.user).count()
    else:
        wishlist_session = request.session.get('wishlist_ids', [])
        wishlist_count = len(wishlist_session)

    # Active top categories for quick navigation
    categories = Category.objects.filter(is_active=True, parent__isnull=True).order_by('display_order', 'name')[:8]

    # Superadmin KPI stats (calculated only when accessed by a superuser)
    superadmin_stats = None
    if request.user.is_authenticated and request.user.is_superuser:
        superadmin_stats = {
            'total_stores': Store.objects.count(),
            'pending_stores': Store.objects.filter(status='PENDING').count(),
            'active_stores': Store.objects.filter(status='ACTIVE').count(),
            'total_tiers': MerchantTier.objects.count(),
            'total_services': PlatformService.objects.count(),
            'active_services': PlatformService.objects.filter(is_global_enabled=True).count(),
            'platform_commission': store_setting.platform_commission_percent,
            'maintenance_mode': store_setting.maintenance_mode,
        }

    return {
        'brand_name': 'OHUAMI',
        'brand_tagline': 'Your market. Your business. Your growth.',
        'brand_secondary': 'Commerce made for your ambition.',
        'parent_company': 'Cube Tech Enterprises',
        'brand_colors': {
            'red': '#E53935',
            'black': '#111111',
            'yellow': '#FFC928',
            'white': '#FFFFFF',
            'neutral_light': '#F8F9FA',
            'neutral_border': '#E5E7EB',
            'neutral_text': '#6B7280',
            'success_green': '#10B981',
        },
        'store_setting': store_setting,
        'cart_count': cart_count,
        'cart': cart,
        'wishlist_count': wishlist_count,
        'header_categories': categories,
        'currency_symbol': store_setting.currency_symbol,
        'paystack_public_key': getattr(settings, 'PAYSTACK_PUBLIC_KEY', 'pk_test_sample_cubetech'),
        'superadmin_stats': superadmin_stats,
    }
