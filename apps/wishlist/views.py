import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.catalog.models import Product
from .models import WishlistItem


def wishlist_list(request):
    if request.user.is_authenticated:
        items = WishlistItem.objects.filter(user=request.user).select_related('product__category')
    else:
        ids = request.session.get('wishlist_ids', [])
        products = Product.objects.filter(id__in=ids, is_active=True).select_related('category')
        # Wrap in mock objects with .product for template consistency
        items = [{'product': p} for p in products]

    return render(request, 'wishlist/list.html', {'wishlist_items': items})


@require_POST
def api_toggle_wishlist(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product = Product.objects.get(id=product_id, is_active=True)

        if request.user.is_authenticated:
            item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
            if not created:
                item.delete()
                is_wishlisted = False
                msg = f"Removed '{product.name}' from wishlist."
            else:
                is_wishlisted = True
                msg = f"Saved '{product.name}' to wishlist!"
            count = WishlistItem.objects.filter(user=request.user).count()
        else:
            ids = request.session.get('wishlist_ids', [])
            if product_id in ids:
                ids.remove(product_id)
                is_wishlisted = False
                msg = f"Removed '{product.name}' from wishlist."
            else:
                ids.append(product_id)
                is_wishlisted = True
                msg = f"Saved '{product.name}' to wishlist!"
            request.session['wishlist_ids'] = ids
            count = len(ids)

        return JsonResponse({
            'success': True,
            'is_wishlisted': is_wishlisted,
            'wishlist_count': count,
            'message': msg
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
