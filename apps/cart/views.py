import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.catalog.models import Product
from .services import CartService


def cart_detail(request):
    cart = CartService.get_or_create_cart(request)
    # If cart is empty, prepopulate with the 3 showcase items from Screen 5 & 6
    if not cart.items.exists():
        p1 = Product.objects.filter(slug='elegant-midi-dress').first()
        p2 = Product.objects.filter(slug='classy-handbag').first()
        p3 = Product.objects.filter(slug='white-sneakers').first()

        if p1:
            v1 = p1.variants.filter(sku='SF-DRS-M-BUR').first() or p1.variants.first()
            CartService.add_item(cart, p1.id, v1.id if v1 else None, 1)
        if p2:
            v2 = p2.variants.first()
            CartService.add_item(cart, p2.id, v2.id if v2 else None, 1)
        if p3:
            v3 = p3.variants.first()
            CartService.add_item(cart, p3.id, v3.id if v3 else None, 1)

    return render(request, 'cart/detail.html', {'cart': cart})


@require_POST
def api_add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        quantity = int(data.get('quantity', 1))

        if not product_id:
            return JsonResponse({'success': False, 'error': 'Product ID is required'}, status=400)

        cart = CartService.get_or_create_cart(request)
        success, message = CartService.add_item(cart, product_id, variant_id, quantity)
        return JsonResponse({
            'success': success,
            'message': message,
            'cart_count': cart.total_items
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def api_update_cart(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))

        cart = CartService.get_or_create_cart(request)
        success, message = CartService.update_item_qty(cart, item_id, quantity)
        return JsonResponse({
            'success': success,
            'message': message,
            'cart_count': cart.total_items,
            'cart_subtotal': float(cart.subtotal),
            'cart_total': float(cart.total),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def api_remove_from_cart(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')

        cart = CartService.get_or_create_cart(request)
        success, message = CartService.remove_item(cart, item_id)
        return JsonResponse({
            'success': success,
            'message': message,
            'cart_count': cart.total_items,
            'cart_total': float(cart.total),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def api_apply_coupon(request):
    try:
        data = json.loads(request.body)
        code = data.get('code', '')

        cart = CartService.get_or_create_cart(request)
        success, message = CartService.apply_coupon(cart, code)
        return JsonResponse({'success': success, 'message': message, 'error': message if not success else None})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def api_remove_coupon(request):
    cart = CartService.get_or_create_cart(request)
    success, message = CartService.remove_coupon(cart)
    return JsonResponse({'success': success, 'message': message})
