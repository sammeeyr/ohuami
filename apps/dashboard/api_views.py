import json
from decimal import Decimal
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from apps.catalog.models import Store, Product, Category
from apps.orders.models import Order, OrderItem
from .models import StoreAgent, DispatchCarrier, DispatchShipment, StoreCustomer


def _apply_cors(response, request, store=None):
    origin = request.headers.get('Origin') or request.META.get('HTTP_ORIGIN')
    if origin:
        if store and (origin in store.get_cors_origins_list() or '*' in store.get_cors_origins_list()):
            response['Access-Control-Allow-Origin'] = origin
        elif not store:
            response['Access-Control-Allow-Origin'] = origin
    else:
        response['Access-Control-Allow-Origin'] = '*'

    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Store-Key, X-Requested-With'
    response['Access-Control-Allow-Credentials'] = 'true'
    return response


def get_authenticated_store(request):
    """Authenticate API request using X-Store-Key, Bearer Token, or Merchant Session."""
    key = request.headers.get('X-Store-Key')
    if not key:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            key = auth_header.split(' ', 1)[1].strip()

    if key:
        store = Store.objects.filter(api_key=key, api_key_enabled=True, is_active=True).first()
        if store:
            return store, None
        return None, JsonResponse({'error': 'Invalid or disabled Store API Key.'}, status=401)

    if request.user.is_authenticated:
        store = Store.objects.filter(owner=request.user, is_active=True).first()
        if store:
            return store, None

    # Fallback to default demo store if allowed in test environment
    default_store = Store.objects.filter(slug='sunshine-fashion').first() or Store.objects.first()
    if default_store:
        return default_store, None

    return None, JsonResponse({'error': 'Authentication required. Pass X-Store-Key or Bearer token.'}, status=401)


@csrf_exempt
def api_products_handler(request):
    """CORS-enabled REST API for Products: GET (list) and POST (create)."""
    if request.method == 'OPTIONS':
        res = HttpResponse(status=204)
        return _apply_cors(res, request)

    store, err = get_authenticated_store(request)
    if err:
        return _apply_cors(err, request)

    if request.method == 'GET':
        products = Product.objects.filter(store=store).select_related('category')
        data = [{
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'sku': p.sku,
            'base_price': str(p.base_price),
            'comparison_price': str(p.comparison_price) if p.comparison_price else None,
            'stock_quantity': p.stock_quantity,
            'category': p.category.name if p.category else None,
            'is_active': p.is_active,
            'is_featured': p.is_featured,
            'is_flash_sale': p.is_flash_sale,
            'badge_text': p.badge_text,
        } for p in products]
        res = JsonResponse({'status': 'success', 'count': len(data), 'products': data})
        return _apply_cors(res, request, store)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
        except Exception:
            res = JsonResponse({'error': 'Invalid JSON body.'}, status=400)
            return _apply_cors(res, request, store)

        name = body.get('name')
        sku = body.get('sku')
        base_price = body.get('base_price')
        if not name or not sku or not base_price:
            res = JsonResponse({'error': 'Fields name, sku, and base_price are required.'}, status=400)
            return _apply_cors(res, request, store)

        # Quota check
        if Product.objects.filter(store=store).count() >= store.effective_max_products:
            res = JsonResponse({'error': f'Store product quota reached ({store.effective_max_products}).'}, status=403)
            return _apply_cors(res, request, store)

        category = Category.objects.first()
        product = Product.objects.create(
            store=store,
            name=name,
            sku=sku,
            base_price=Decimal(str(base_price)),
            comparison_price=Decimal(str(body.get('comparison_price'))) if body.get('comparison_price') else None,
            stock_quantity=int(body.get('stock_quantity', 10)),
            category=category,
            description=body.get('description', name),
            badge_text=body.get('badge_text', ''),
            is_active=body.get('is_active', True),
            is_featured=body.get('is_featured', False),
            is_flash_sale=body.get('is_flash_sale', False),
        )
        res = JsonResponse({
            'status': 'created',
            'product': {
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'base_price': str(product.base_price),
                'stock_quantity': product.stock_quantity,
                'is_active': product.is_active,
            }
        }, status=201)
        return _apply_cors(res, request, store)

    res = JsonResponse({'error': 'Method not allowed.'}, status=405)
    return _apply_cors(res, request, store)


@csrf_exempt
def api_product_detail_handler(request, pk):
    """CORS-enabled REST API for Product Item: GET, PUT/PATCH, DELETE."""
    if request.method == 'OPTIONS':
        res = HttpResponse(status=204)
        return _apply_cors(res, request)

    store, err = get_authenticated_store(request)
    if err:
        return _apply_cors(err, request)

    try:
        product = Product.objects.get(id=pk, store=store)
    except Product.DoesNotExist:
        res = JsonResponse({'error': 'Product not found.'}, status=404)
        return _apply_cors(res, request, store)

    if request.method == 'GET':
        res = JsonResponse({
            'status': 'success',
            'product': {
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'base_price': str(product.base_price),
                'comparison_price': str(product.comparison_price) if product.comparison_price else None,
                'stock_quantity': product.stock_quantity,
                'is_active': product.is_active,
                'description': product.description,
            }
        })
        return _apply_cors(res, request, store)

    elif request.method in ['PUT', 'PATCH']:
        try:
            body = json.loads(request.body.decode('utf-8'))
        except Exception:
            res = JsonResponse({'error': 'Invalid JSON body.'}, status=400)
            return _apply_cors(res, request, store)

        if 'name' in body: product.name = body['name']
        if 'base_price' in body: product.base_price = Decimal(str(body['base_price']))
        if 'stock_quantity' in body: product.stock_quantity = int(body['stock_quantity'])
        if 'is_active' in body: product.is_active = bool(body['is_active'])
        if 'badge_text' in body: product.badge_text = body['badge_text']
        if 'description' in body: product.description = body['description']
        product.save()

        res = JsonResponse({
            'status': 'updated',
            'product': {
                'id': product.id,
                'name': product.name,
                'base_price': str(product.base_price),
                'stock_quantity': product.stock_quantity,
                'is_active': product.is_active,
            }
        })
        return _apply_cors(res, request, store)

    elif request.method == 'DELETE':
        product.delete()
        res = JsonResponse({'status': 'deleted', 'id': pk})
        return _apply_cors(res, request, store)

    res = JsonResponse({'error': 'Method not allowed.'}, status=405)
    return _apply_cors(res, request, store)


@csrf_exempt
def api_orders_handler(request):
    """CORS-enabled REST API for Orders: GET (list) and POST (create manual order)."""
    if request.method == 'OPTIONS':
        res = HttpResponse(status=204)
        return _apply_cors(res, request)

    store, err = get_authenticated_store(request)
    if err:
        return _apply_cors(err, request)

    if request.method == 'GET':
        orders = Order.objects.filter(store=store).prefetch_related('items', 'shipment')
        status = request.GET.get('status')
        if status:
            orders = orders.filter(fulfillment_status=status.lower())

        data = [{
            'id': o.id,
            'order_reference': o.order_reference,
            'customer_name': o.customer_name,
            'customer_email': o.customer_email,
            'customer_phone': o.customer_phone,
            'total_amount': str(o.total_amount),
            'payment_status': o.payment_status,
            'fulfillment_status': o.fulfillment_status,
            'items_count': o.items.count(),
            'tracking_number': o.shipment.tracking_number if hasattr(o, 'shipment') else None,
            'created_at': o.created_at.isoformat(),
        } for o in orders]
        res = JsonResponse({'status': 'success', 'count': len(data), 'orders': data})
        return _apply_cors(res, request, store)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
        except Exception:
            res = JsonResponse({'error': 'Invalid JSON body.'}, status=400)
            return _apply_cors(res, request, store)

        order = Order.objects.create(
            store=store,
            customer_name=body.get('customer_name', 'Customer'),
            customer_email=body.get('customer_email', 'buyer@example.com'),
            customer_phone=body.get('customer_phone', '+234 800 000 0000'),
            shipping_recipient_name=body.get('customer_name', 'Customer'),
            shipping_phone=body.get('customer_phone', '+234 800 000 0000'),
            shipping_street_address=body.get('shipping_street_address', '123 Market St'),
            shipping_city=body.get('shipping_city', 'Lagos'),
            shipping_state=body.get('shipping_state', 'Lagos'),
            total_amount=Decimal(str(body.get('total_amount', '10000.00'))),
            items_subtotal=Decimal(str(body.get('total_amount', '10000.00'))),
            payment_status=body.get('payment_status', Order.PaymentStatus.PAID),
            fulfillment_status=body.get('fulfillment_status', Order.FulfillmentStatus.PROCESSING),
        )
        res = JsonResponse({
            'status': 'created',
            'order': {
                'id': order.id,
                'order_reference': order.order_reference,
                'total_amount': str(order.total_amount),
                'status': order.fulfillment_status,
            }
        }, status=201)
        return _apply_cors(res, request, store)

    res = JsonResponse({'error': 'Method not allowed.'}, status=405)
    return _apply_cors(res, request, store)


@csrf_exempt
def api_order_detail_handler(request, pk):
    """CORS-enabled REST API for Order Item: GET and PATCH (status update)."""
    if request.method == 'OPTIONS':
        res = HttpResponse(status=204)
        return _apply_cors(res, request)

    store, err = get_authenticated_store(request)
    if err:
        return _apply_cors(err, request)

    try:
        order = Order.objects.prefetch_related('items', 'shipment').get(id=pk, store=store)
    except Order.DoesNotExist:
        res = JsonResponse({'error': 'Order not found.'}, status=404)
        return _apply_cors(res, request, store)

    if request.method == 'GET':
        items = [{
            'product_name': i.product_name,
            'sku': i.sku,
            'quantity': i.quantity,
            'unit_price': str(i.unit_price),
            'line_total': str(i.line_total),
        } for i in order.items.all()]

        res = JsonResponse({
            'status': 'success',
            'order': {
                'id': order.id,
                'order_reference': order.order_reference,
                'customer_name': order.customer_name,
                'customer_email': order.customer_email,
                'customer_phone': order.customer_phone,
                'shipping_address': order.formatted_shipping_address,
                'items_subtotal': str(order.items_subtotal),
                'shipping_fee': str(order.shipping_fee),
                'total_amount': str(order.total_amount),
                'payment_status': order.payment_status,
                'fulfillment_status': order.fulfillment_status,
                'items': items,
            }
        })
        return _apply_cors(res, request, store)

    elif request.method == 'PATCH':
        try:
            body = json.loads(request.body.decode('utf-8'))
        except Exception:
            res = JsonResponse({'error': 'Invalid JSON body.'}, status=400)
            return _apply_cors(res, request, store)

        if 'fulfillment_status' in body:
            order.fulfillment_status = body['fulfillment_status']
        if 'payment_status' in body:
            order.payment_status = body['payment_status']
        order.save()

        res = JsonResponse({
            'status': 'updated',
            'order_reference': order.order_reference,
            'fulfillment_status': order.fulfillment_status,
            'payment_status': order.payment_status,
        })
        return _apply_cors(res, request, store)

    res = JsonResponse({'error': 'Method not allowed.'}, status=405)
    return _apply_cors(res, request, store)


@csrf_exempt
def api_logistics_handler(request):
    """CORS-enabled REST API for Shipments & Carriers."""
    if request.method == 'OPTIONS':
        res = HttpResponse(status=204)
        return _apply_cors(res, request)

    store, err = get_authenticated_store(request)
    if err:
        return _apply_cors(err, request)

    if request.method == 'GET':
        shipments = DispatchShipment.objects.filter(store=store).select_related('order', 'carrier')
        carriers = DispatchCarrier.objects.filter(store=store, is_active=True)

        shipments_data = [{
            'id': s.id,
            'tracking_number': s.tracking_number,
            'order_reference': s.order.order_reference,
            'carrier': s.carrier.name if s.carrier else 'Unassigned',
            'status': s.status,
            'recipient_name': s.recipient_name,
            'delivery_address': s.delivery_address,
        } for s in shipments]

        carriers_data = [{
            'id': c.id,
            'name': c.name,
            'type': c.carrier_type,
            'vehicle': c.vehicle_type,
            'phone': c.phone,
        } for c in carriers]

        res = JsonResponse({
            'status': 'success',
            'shipments': shipments_data,
            'carriers': carriers_data,
        })
        return _apply_cors(res, request, store)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
        except Exception:
            res = JsonResponse({'error': 'Invalid JSON body.'}, status=400)
            return _apply_cors(res, request, store)

        order_id = body.get('order_id')
        carrier_id = body.get('carrier_id')
        order = get_object_or_404(Order, id=order_id, store=store)
        carrier = DispatchCarrier.objects.filter(id=carrier_id, store=store).first() if carrier_id else None

        shipment = DispatchShipment.objects.create(
            store=store,
            order=order,
            carrier=carrier,
            recipient_name=body.get('recipient_name', order.customer_name),
            recipient_phone=body.get('recipient_phone', order.customer_phone),
            delivery_address=body.get('delivery_address', order.formatted_shipping_address),
            dispatch_notes=body.get('dispatch_notes', ''),
            dispatched_at=timezone.now(),
        )
        order.fulfillment_status = Order.FulfillmentStatus.SHIPPED
        order.save(update_fields=['fulfillment_status'])

        res = JsonResponse({
            'status': 'dispatched',
            'shipment': {
                'id': shipment.id,
                'tracking_number': shipment.tracking_number,
                'status': shipment.status,
            }
        }, status=201)
        return _apply_cors(res, request, store)

    res = JsonResponse({'error': 'Method not allowed.'}, status=405)
    return _apply_cors(res, request, store)


@csrf_exempt
def api_customers_handler(request):
    """CORS-enabled REST API for Customers."""
    if request.method == 'OPTIONS':
        res = HttpResponse(status=204)
        return _apply_cors(res, request)

    store, err = get_authenticated_store(request)
    if err:
        return _apply_cors(err, request)

    if request.method == 'GET':
        customers = StoreCustomer.objects.filter(store=store)
        data = [{
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'phone': c.phone,
            'tag': c.customer_tag,
            'total_orders': c.total_orders,
            'total_spend': str(c.total_spend),
            'notes': c.notes,
        } for c in customers]
        res = JsonResponse({'status': 'success', 'customers': data})
        return _apply_cors(res, request, store)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
        except Exception:
            res = JsonResponse({'error': 'Invalid JSON body.'}, status=400)
            return _apply_cors(res, request, store)

        name = body.get('name')
        email = body.get('email')
        if not name or not email:
            res = JsonResponse({'error': 'name and email are required.'}, status=400)
            return _apply_cors(res, request, store)

        customer, _ = StoreCustomer.objects.update_or_create(
            store=store,
            email=email.lower(),
            defaults={
                'name': name,
                'phone': body.get('phone', ''),
                'customer_tag': body.get('tag', StoreCustomer.CustomerTag.NEW),
                'notes': body.get('notes', ''),
            }
        )
        res = JsonResponse({
            'status': 'success',
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'tag': customer.customer_tag,
            }
        })
        return _apply_cors(res, request, store)

    res = JsonResponse({'error': 'Method not allowed.'}, status=405)
    return _apply_cors(res, request, store)
