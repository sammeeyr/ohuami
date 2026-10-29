import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from apps.orders.models import Order, OrderItem
from apps.catalog.models import Store, Product, Category, Brand, ProductImage
from apps.promotions.models import Coupon
from .models import StoreAgent, DispatchCarrier, DispatchShipment, StoreCustomer
from .forms import (
    MerchantProductForm,
    MerchantOrderManualCreateForm,
    MerchantStoreSettingsForm,
    MerchantCouponForm,
    StoreAgentForm,
    DispatchCarrierForm,
    DispatchShipmentForm,
    StoreCustomerForm,
    StoreCorsApiForm,
)


def get_current_merchant_store(request):
    if request.user.is_authenticated:
        store = Store.objects.filter(owner=request.user).first()
        if store:
            return store
    return Store.objects.filter(slug='sunshine-fashion').first() or Store.objects.first()


# ==============================================================================
# 1. MERCHANT DASHBOARD HOME
# ==============================================================================

def dashboard_index(request):
    store = get_current_merchant_store(request)

    if store:
        store_orders = Order.objects.filter(store=store)
        store_products = Product.objects.filter(store=store, is_active=True)
    else:
        store_orders = Order.objects.all()
        store_products = Product.objects.filter(is_active=True)

    paid_orders = store_orders.filter(payment_status=Order.PaymentStatus.PAID)
    total_revenue = paid_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('842750.00')

    total_orders = store_orders.count()
    if total_orders == 0:
        total_orders = 36

    total_customers = StoreCustomer.objects.filter(store=store).count()
    if total_customers == 0 and store:
        total_customers = store.followers_count if store.followers_count > 0 else 1248

    products_count = store_products.count()
    if products_count == 0:
        products_count = 52

    recent_orders = store_orders.order_by('-created_at')[:6]

    context = {
        'store': store,
        'merchant_name': store.owner.get_full_name() if (store and store.owner and store.owner.get_full_name()) else "Chinedu Okafor",
        'total_sales': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'products_count': products_count,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/merchant_dashboard.html', context)


# ==============================================================================
# 2. PRODUCTS CRUD
# ==============================================================================

def merchant_products(request):
    """Merchant catalog inventory and product list."""
    store = get_current_merchant_store(request)
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all')

    products = Product.objects.filter(store=store).select_related('category', 'brand').order_by('-created_at')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    if status_filter == 'active':
        products = products.filter(is_active=True)
    elif status_filter == 'inactive':
        products = products.filter(is_active=False)

    max_limit = store.effective_max_products
    is_at_limit = products.count() >= max_limit

    context = {
        'store': store,
        'products': products,
        'products_count': products.count(),
        'max_limit': max_limit,
        'is_at_limit': is_at_limit,
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/products.html', context)


def merchant_product_create(request):
    """Add a new product to merchant catalog with image uploads."""
    store = get_current_merchant_store(request)
    current_count = Product.objects.filter(store=store).count()
    max_limit = store.effective_max_products

    if current_count >= max_limit:
        messages.error(request, f"Your {store.plan} product quota ({max_limit} products) has been reached. Please upgrade your store tier.")
        return redirect('dashboard:products')

    if request.method == 'POST':
        form = MerchantProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.seller_name = store.name
            product.save()

            # 1. Primary image upload
            if 'primary_image' in request.FILES:
                ProductImage.objects.create(
                    product=product,
                    image=request.FILES['primary_image'],
                    is_primary=True,
                    display_order=0,
                )

            # 2. Additional gallery images upload
            for idx, img_file in enumerate(request.FILES.getlist('additional_images')):
                ProductImage.objects.create(
                    product=product,
                    image=img_file,
                    is_primary=False,
                    display_order=idx + 1,
                )

            messages.success(request, f"Product '{product.name}' was created successfully!")
            return redirect('dashboard:products')
        else:
            messages.error(request, "Failed to create product. Please check the required fields.")
    else:
        form = MerchantProductForm()

    context = {
        'store': store,
        'form': form,
        'is_editing': False,
        'categories': Category.objects.filter(is_active=True),
    }
    return render(request, 'dashboard/product_create.html', context)


def merchant_product_edit(request, product_id):
    """Update an existing product and its image gallery."""
    store = get_current_merchant_store(request)
    product = get_object_or_404(Product.objects.prefetch_related('images'), id=product_id, store=store)

    if request.method == 'POST':
        form = MerchantProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            # Handle new primary image upload
            if 'primary_image' in request.FILES:
                product.images.filter(is_primary=True).update(is_primary=False)
                ProductImage.objects.create(
                    product=product,
                    image=request.FILES['primary_image'],
                    is_primary=True,
                    display_order=0,
                )

            # Handle additional gallery images upload
            existing_count = product.images.count()
            for idx, img_file in enumerate(request.FILES.getlist('additional_images')):
                ProductImage.objects.create(
                    product=product,
                    image=img_file,
                    is_primary=False,
                    display_order=existing_count + idx,
                )

            messages.success(request, f"Product '{product.name}' was updated successfully!")
            return redirect('dashboard:product_edit', product_id=product.id)
        else:
            messages.error(request, "Failed to update product. Please check your entries.")
    else:
        form = MerchantProductForm(instance=product)

    context = {
        'store': store,
        'form': form,
        'product': product,
        'existing_images': product.images.all(),
        'is_editing': True,
        'categories': Category.objects.filter(is_active=True),
    }
    return render(request, 'dashboard/product_create.html', context)


@require_POST
def merchant_product_image_delete(request, product_id, image_id):
    """Delete an individual gallery image from a product."""
    store = get_current_merchant_store(request)
    product = get_object_or_404(Product, id=product_id, store=store)
    image = get_object_or_404(ProductImage, id=image_id, product=product)
    image.delete()
    messages.success(request, "Image was removed from product gallery.")
    return redirect('dashboard:product_edit', product_id=product.id)


@require_POST
def merchant_product_image_set_primary(request, product_id, image_id):
    """Set an image as the primary cover photo for the product."""
    store = get_current_merchant_store(request)
    product = get_object_or_404(Product, id=product_id, store=store)
    product.images.all().update(is_primary=False)
    image = get_object_or_404(ProductImage, id=image_id, product=product)
    image.is_primary = True
    image.save(update_fields=['is_primary'])
    messages.success(request, "Primary cover photo updated successfully!")
    return redirect('dashboard:product_edit', product_id=product.id)


@require_POST
def merchant_product_delete(request, product_id):
    """Delete a product from the merchant catalog."""
    store = get_current_merchant_store(request)
    product = get_object_or_404(Product, id=product_id, store=store)
    product_name = product.name
    product.delete()
    messages.success(request, f"Product '{product_name}' was permanently removed from your catalog.")
    return redirect('dashboard:products')


@require_POST
def merchant_product_toggle_status(request, product_id):
    """Quickly toggle a product between active and inactive."""
    store = get_current_merchant_store(request)
    product = get_object_or_404(Product, id=product_id, store=store)
    product.is_active = not product.is_active
    product.save(update_fields=['is_active'])
    status_str = "Active" if product.is_active else "Inactive"
    messages.success(request, f"Product '{product.name}' is now {status_str}.")
    return redirect('dashboard:products')


# ==============================================================================
# 3. ORDERS CRUD & MANAGEMENT
# ==============================================================================

def merchant_orders(request):
    """Store customer orders management."""
    store = get_current_merchant_store(request)
    status_filter = request.GET.get('status', 'ALL')
    query = request.GET.get('q', '').strip()

    orders = Order.objects.filter(store=store).prefetch_related('items', 'shipment').order_by('-created_at')

    if status_filter != 'ALL':
        orders = orders.filter(fulfillment_status=status_filter.lower())

    if query:
        orders = orders.filter(
            Q(order_reference__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(customer_email__icontains=query) |
            Q(customer_phone__icontains=query)
        )

    context = {
        'store': store,
        'orders': orders,
        'current_status': status_filter,
        'query': query,
    }
    return render(request, 'dashboard/orders.html', context)


def merchant_order_detail(request, order_id):
    """Detailed view of a single order for the merchant."""
    store = get_current_merchant_store(request)
    order = get_object_or_404(Order.objects.prefetch_related('items', 'items__product'), id=order_id, store=store)
    carriers = DispatchCarrier.objects.filter(store=store, is_active=True)

    shipment = getattr(order, 'shipment', None)

    context = {
        'store': store,
        'order': order,
        'shipment': shipment,
        'carriers': carriers,
    }
    return render(request, 'dashboard/order_detail.html', context)


def merchant_order_create(request):
    """Create manual order for in-person, phone, or WhatsApp sales."""
    store = get_current_merchant_store(request)

    if request.method == 'POST':
        form = MerchantOrderManualCreateForm(request.POST, store=store)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            shipping_fee = form.cleaned_data['shipping_fee']
            unit_price = product.base_price
            items_subtotal = unit_price * quantity
            total_amount = items_subtotal + shipping_fee

            # Create Order
            order = Order.objects.create(
                store=store,
                customer_name=form.cleaned_data['customer_name'],
                customer_email=form.cleaned_data['customer_email'],
                customer_phone=form.cleaned_data['customer_phone'],
                shipping_recipient_name=form.cleaned_data['customer_name'],
                shipping_phone=form.cleaned_data['customer_phone'],
                shipping_street_address=form.cleaned_data['shipping_street_address'],
                shipping_city=form.cleaned_data['shipping_city'],
                shipping_state=form.cleaned_data['shipping_state'],
                shipping_country='Nigeria',
                currency='NGN',
                items_subtotal=items_subtotal,
                shipping_fee=shipping_fee,
                total_amount=total_amount,
                payment_method=form.cleaned_data['payment_method'],
                payment_status=form.cleaned_data['payment_status'],
                fulfillment_status=form.cleaned_data['fulfillment_status'],
                paid_at=timezone.now() if form.cleaned_data['payment_status'] == Order.PaymentStatus.PAID else None,
            )

            # Create Order Item
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                sku=product.sku,
                unit_price=unit_price,
                quantity=quantity,
                line_total=items_subtotal,
            )

            # Deduct stock
            if product.stock_quantity >= quantity:
                product.stock_quantity -= quantity
                product.save(update_fields=['stock_quantity'])

            # Record customer relationship
            StoreCustomer.objects.get_or_create(
                store=store,
                email=order.customer_email.lower(),
                defaults={
                    'name': order.customer_name,
                    'phone': order.customer_phone,
                    'customer_tag': StoreCustomer.CustomerTag.NEW,
                }
            )

            messages.success(request, f"Manual order #{order.order_reference} registered successfully!")
            return redirect('dashboard:order_detail', order_id=order.id)
        else:
            messages.error(request, "Failed to create order. Please check the fields.")
    else:
        form = MerchantOrderManualCreateForm(store=store)

    context = {
        'store': store,
        'form': form,
    }
    return render(request, 'dashboard/order_create.html', context)


@require_POST
def merchant_update_order_status(request, order_id):
    """Update order fulfillment and payment status."""
    store = get_current_merchant_store(request)
    order = get_object_or_404(Order, id=order_id, store=store)

    fulfillment_status = request.POST.get('status') or request.POST.get('fulfillment_status')
    payment_status = request.POST.get('payment_status')

    if fulfillment_status and fulfillment_status in dict(Order.FulfillmentStatus.choices):
        order.fulfillment_status = fulfillment_status

    if payment_status and payment_status in dict(Order.PaymentStatus.choices):
        order.payment_status = payment_status
        if payment_status == Order.PaymentStatus.PAID and not order.paid_at:
            order.paid_at = timezone.now()

    order.save()
    messages.success(request, f"Order #{order.order_reference} status updated successfully.")
    
    redirect_target = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if redirect_target:
        return redirect(redirect_target)
    return redirect('dashboard:orders')


@require_POST
def merchant_order_cancel(request, order_id):
    """Cancel an order and return inventory."""
    store = get_current_merchant_store(request)
    order = get_object_or_404(Order, id=order_id, store=store)

    if order.order_status != Order.OrderStatus.CANCELLED:
        order.order_status = Order.OrderStatus.CANCELLED
        order.fulfillment_status = Order.FulfillmentStatus.UNFULFILLED
        order.payment_status = Order.PaymentStatus.CANCELLED
        order.save()

        # Restock items
        for item in order.items.all():
            if item.product:
                item.product.stock_quantity += item.quantity
                item.product.save(update_fields=['stock_quantity'])

        messages.success(request, f"Order #{order.order_reference} was cancelled and inventory was restocked.")
    return redirect('dashboard:order_detail', order_id=order.id)


# ==============================================================================
# 4. AGENTS / STAFF MANAGEMENT
# ==============================================================================

def merchant_agents(request):
    """Store staff members and support agents directory."""
    store = get_current_merchant_store(request)
    agents = StoreAgent.objects.filter(store=store).order_by('-created_at')

    # Quota check
    max_staff = store.tier.max_staff_accounts if store.tier else 5
    is_at_limit = agents.count() >= max_staff

    context = {
        'store': store,
        'agents': agents,
        'agents_count': agents.count(),
        'max_staff': max_staff,
        'is_at_limit': is_at_limit,
    }
    return render(request, 'dashboard/agents.html', context)


def merchant_agent_create(request):
    """Add / invite a staff member or support agent."""
    store = get_current_merchant_store(request)
    max_staff = store.tier.max_staff_accounts if store.tier else 5

    if StoreAgent.objects.filter(store=store).count() >= max_staff:
        messages.error(request, f"You have reached your staff accounts limit ({max_staff} staff). Please upgrade your merchant tier.")
        return redirect('dashboard:agents')

    if request.method == 'POST':
        form = StoreAgentForm(request.POST)
        if form.is_valid():
            agent = form.save(commit=False)
            agent.store = store
            agent.save()
            messages.success(request, f"Agent '{agent.name}' was added to your store team!")
            return redirect('dashboard:agents')
        else:
            messages.error(request, "Failed to add agent. Email may already be registered.")
    else:
        form = StoreAgentForm()

    context = {
        'store': store,
        'form': form,
        'is_editing': False,
    }
    return render(request, 'dashboard/agent_form.html', context)


def merchant_agent_edit(request, agent_id):
    """Edit agent role and permissions."""
    store = get_current_merchant_store(request)
    agent = get_object_or_404(StoreAgent, id=agent_id, store=store)

    if request.method == 'POST':
        form = StoreAgentForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            messages.success(request, f"Agent '{agent.name}' updated successfully.")
            return redirect('dashboard:agents')
        else:
            messages.error(request, "Failed to update agent. Please check your entries.")
    else:
        form = StoreAgentForm(instance=agent)

    context = {
        'store': store,
        'form': form,
        'agent': agent,
        'is_editing': True,
    }
    return render(request, 'dashboard/agent_form.html', context)


@require_POST
def merchant_agent_delete(request, agent_id):
    """Remove a staff agent."""
    store = get_current_merchant_store(request)
    agent = get_object_or_404(StoreAgent, id=agent_id, store=store)
    agent_name = agent.name
    agent.delete()
    messages.success(request, f"Agent '{agent_name}' was removed from your store team.")
    return redirect('dashboard:agents')


@require_POST
def merchant_agent_toggle_status(request, agent_id):
    """Toggle agent active/inactive state."""
    store = get_current_merchant_store(request)
    agent = get_object_or_404(StoreAgent, id=agent_id, store=store)
    agent.is_active = not agent.is_active
    agent.save(update_fields=['is_active'])
    status_str = "Active" if agent.is_active else "Suspended"
    messages.success(request, f"Agent '{agent.name}' is now {status_str}.")
    return redirect('dashboard:agents')


# ==============================================================================
# 5. DISPATCH & LOGISTICS MANAGEMENT
# ==============================================================================

def merchant_logistics(request):
    """Logistics & Dispatch hub: shipments, carriers, and delivery tracking."""
    store = get_current_merchant_store(request)
    shipments = DispatchShipment.objects.filter(store=store).select_related('order', 'carrier').order_by('-created_at')
    carriers = DispatchCarrier.objects.filter(store=store).order_by('-created_at')

    # Metrics
    active_shipments_count = shipments.exclude(status__in=[DispatchShipment.Status.DELIVERED, DispatchShipment.Status.RETURNED]).count()
    in_transit_count = shipments.filter(status=DispatchShipment.Status.IN_TRANSIT).count()
    delivered_count = shipments.filter(status=DispatchShipment.Status.DELIVERED).count()
    active_carriers_count = carriers.filter(is_active=True).count()

    context = {
        'store': store,
        'shipments': shipments,
        'carriers': carriers,
        'active_shipments_count': active_shipments_count,
        'in_transit_count': in_transit_count,
        'delivered_count': delivered_count,
        'active_carriers_count': active_carriers_count,
    }
    return render(request, 'dashboard/logistics.html', context)


def merchant_carrier_create(request):
    """Register a new delivery rider or third-party logistics courier."""
    store = get_current_merchant_store(request)

    if request.method == 'POST':
        form = DispatchCarrierForm(request.POST)
        if form.is_valid():
            carrier = form.save(commit=False)
            carrier.store = store
            carrier.save()
            messages.success(request, f"Carrier/Rider '{carrier.name}' registered successfully!")
            return redirect('dashboard:logistics')
        else:
            messages.error(request, "Failed to register carrier. Please check required fields.")
    else:
        form = DispatchCarrierForm()

    context = {
        'store': store,
        'form': form,
        'is_editing': False,
    }
    return render(request, 'dashboard/carrier_form.html', context)


def merchant_carrier_edit(request, carrier_id):
    """Edit carrier or delivery rider details."""
    store = get_current_merchant_store(request)
    carrier = get_object_or_404(DispatchCarrier, id=carrier_id, store=store)

    if request.method == 'POST':
        form = DispatchCarrierForm(request.POST, instance=carrier)
        if form.is_valid():
            form.save()
            messages.success(request, f"Carrier '{carrier.name}' updated successfully.")
            return redirect('dashboard:logistics')
        else:
            messages.error(request, "Failed to update carrier. Please check entries.")
    else:
        form = DispatchCarrierForm(instance=carrier)

    context = {
        'store': store,
        'form': form,
        'carrier': carrier,
        'is_editing': True,
    }
    return render(request, 'dashboard/carrier_form.html', context)


@require_POST
def merchant_carrier_delete(request, carrier_id):
    """Remove a delivery courier or rider."""
    store = get_current_merchant_store(request)
    carrier = get_object_or_404(DispatchCarrier, id=carrier_id, store=store)
    carrier_name = carrier.name
    carrier.delete()
    messages.success(request, f"Carrier '{carrier_name}' removed.")
    return redirect('dashboard:logistics')


def merchant_dispatch_create(request):
    """Assign an order to dispatch and generate a tracking number."""
    store = get_current_merchant_store(request)
    order_id = request.GET.get('order_id')
    selected_order = None
    if order_id:
        selected_order = get_object_or_404(Order, id=order_id, store=store)

    if request.method == 'POST':
        target_order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=target_order_id, store=store)

        # Check if already dispatched
        if hasattr(order, 'shipment'):
            messages.info(request, f"Order #{order.order_reference} already has a dispatch tracking number ({order.shipment.tracking_number}).")
            return redirect('dashboard:logistics')

        form = DispatchShipmentForm(request.POST, store=store)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.store = store
            shipment.order = order
            shipment.dispatched_at = timezone.now()
            shipment.save()

            # Automatically advance order fulfillment status to Shipped
            order.fulfillment_status = Order.FulfillmentStatus.SHIPPED
            order.save(update_fields=['fulfillment_status'])

            messages.success(request, f"Order #{order.order_reference} dispatched! Tracking: {shipment.tracking_number}")
            return redirect('dashboard:logistics')
        else:
            messages.error(request, "Failed to create shipment. Please verify details.")
    else:
        initial_data = {}
        if selected_order:
            initial_data = {
                'delivery_address': selected_order.formatted_shipping_address,
                'recipient_name': selected_order.shipping_recipient_name or selected_order.customer_name,
                'recipient_phone': selected_order.shipping_phone or selected_order.customer_phone,
            }
        form = DispatchShipmentForm(initial=initial_data, store=store)

    # Orders available for dispatch (not yet dispatched)
    available_orders = Order.objects.filter(store=store, shipment__isnull=True).order_by('-created_at')

    context = {
        'store': store,
        'form': form,
        'selected_order': selected_order,
        'available_orders': available_orders,
    }
    return render(request, 'dashboard/dispatch_create.html', context)


@require_POST
def merchant_dispatch_update_status(request, shipment_id):
    """Advance dispatch status (In Transit, Out for Delivery, Delivered)."""
    store = get_current_merchant_store(request)
    shipment = get_object_or_404(DispatchShipment, id=shipment_id, store=store)

    new_status = request.POST.get('status')
    if new_status in dict(DispatchShipment.Status.choices):
        shipment.status = new_status
        if new_status == DispatchShipment.Status.DELIVERED:
            shipment.delivered_at = timezone.now()
            shipment.order.fulfillment_status = Order.FulfillmentStatus.DELIVERED
            shipment.order.save(update_fields=['fulfillment_status'])
        elif new_status == DispatchShipment.Status.IN_TRANSIT:
            shipment.order.fulfillment_status = Order.FulfillmentStatus.SHIPPED
            shipment.order.save(update_fields=['fulfillment_status'])

        shipment.save()
        messages.success(request, f"Shipment #{shipment.tracking_number} updated to {shipment.get_status_display()}.")

    return redirect('dashboard:logistics')


# ==============================================================================
# 6. CUSTOMER MANAGEMENT
# ==============================================================================

def merchant_customers(request):
    """Store customer directory and CRM."""
    store = get_current_merchant_store(request)
    query = request.GET.get('q', '').strip()
    tag_filter = request.GET.get('tag', 'all')

    customers = StoreCustomer.objects.filter(store=store).order_by('-created_at')

    if query:
        customers = customers.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )
    if tag_filter != 'all':
        customers = customers.filter(customer_tag=tag_filter)

    context = {
        'store': store,
        'customers': customers,
        'customers_count': customers.count(),
        'query': query,
        'tag_filter': tag_filter,
    }
    return render(request, 'dashboard/customers.html', context)


def merchant_customer_detail(request, customer_id):
    """Detailed profile of a customer including all store orders."""
    store = get_current_merchant_store(request)
    customer = get_object_or_404(StoreCustomer, id=customer_id, store=store)

    customer_orders = Order.objects.filter(
        store=store,
        customer_email__iexact=customer.email
    ).prefetch_related('items').order_by('-created_at')

    if request.method == 'POST':
        form = StoreCustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Customer notes for '{customer.name}' updated.")
            return redirect('dashboard:customer_detail', customer_id=customer.id)
    else:
        form = StoreCustomerForm(instance=customer)

    context = {
        'store': store,
        'customer': customer,
        'orders': customer_orders,
        'form': form,
    }
    return render(request, 'dashboard/customer_detail.html', context)


def merchant_customer_create(request):
    """Add a customer record manually."""
    store = get_current_merchant_store(request)

    if request.method == 'POST':
        form = StoreCustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.store = store
            customer.save()
            messages.success(request, f"Customer '{customer.name}' added to your directory!")
            return redirect('dashboard:customers')
        else:
            messages.error(request, "Failed to create customer. Email may already exist.")
    else:
        form = StoreCustomerForm()

    context = {
        'store': store,
        'form': form,
        'is_editing': False,
    }
    return render(request, 'dashboard/customer_form.html', context)


@require_POST
def merchant_customer_delete(request, customer_id):
    """Delete a customer record."""
    store = get_current_merchant_store(request)
    customer = get_object_or_404(StoreCustomer, id=customer_id, store=store)
    customer_name = customer.name
    customer.delete()
    messages.success(request, f"Customer '{customer_name}' removed from directory.")
    return redirect('dashboard:customers')


# ==============================================================================
# 7. CORS & API MANAGEMENT
# ==============================================================================

def merchant_api_cors(request):
    """Store CORS allowed origins and API Key configuration."""
    store = get_current_merchant_store(request)

    if request.method == 'POST':
        form = StoreCorsApiForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, "CORS Allowed Origins and API Key settings saved successfully!")
            return redirect('dashboard:api_cors')
        else:
            messages.error(request, "Could not save CORS configuration. Please verify.")
    else:
        form = StoreCorsApiForm(instance=store)

    origins_list = store.get_cors_origins_list()

    context = {
        'store': store,
        'form': form,
        'origins_list': origins_list,
    }
    return render(request, 'dashboard/api_cors.html', context)


@require_POST
def merchant_api_regenerate_key(request):
    """Regenerate secret API key for store."""
    store = get_current_merchant_store(request)
    new_key = store.regenerate_api_key()
    messages.success(request, f"New Store API Key generated! Keep it secure.")
    return redirect('dashboard:api_cors')


# ==============================================================================
# 8. STORE SETTINGS & DISCOUNTS
# ==============================================================================

def merchant_settings(request):
    """Store profile, banking, and payout configuration."""
    store = get_current_merchant_store(request)

    if request.method == 'POST':
        form = MerchantStoreSettingsForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, f"Store settings for '{store.name}' saved successfully!")
            return redirect('dashboard:settings')
        else:
            messages.error(request, "Could not update settings. Please check your entries.")
    else:
        form = MerchantStoreSettingsForm(instance=store)

    context = {
        'store': store,
        'form': form,
    }
    return render(request, 'dashboard/settings.html', context)


def merchant_discounts(request):
    """Store promotional coupons management."""
    store = get_current_merchant_store(request)
    coupons = Coupon.objects.all().order_by('-start_date')

    if request.method == 'POST':
        form = MerchantCouponForm(request.POST)
        if form.is_valid():
            coupon = form.save()
            messages.success(request, f"Promotional coupon '{coupon.code}' created!")
            return redirect('dashboard:discounts')
        else:
            messages.error(request, "Failed to create coupon. Code must be unique.")
    else:
        form = MerchantCouponForm()

    context = {
        'store': store,
        'coupons': coupons,
        'form': form,
    }
    return render(request, 'dashboard/discounts.html', context)
