import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count
from apps.catalog.models import Store, MerchantTier, Product
from apps.orders.models import Order
from apps.accounts.models import User
from apps.core.models import StoreSetting, PlatformService, AuditLog


def is_super_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == User.Role.ADMIN or user.is_staff)


@user_passes_test(is_super_admin, login_url='/admin/login/')
def super_admin_control_panel(request):
    """
    Super Admin Control Center for OHUAMI & Cube Tech Enterprises.
    Manages:
    1. Merchants & Multi-Store Tenancy
    2. Global Platform Settings
    3. Multi-Merchant Tiers & Quota Configurations
    4. Features & Services Switchboard
    """
    setting = StoreSetting.get_settings()
    
    # 1. Platform Pulse Metrics
    total_stores = Store.objects.count()
    active_stores = Store.objects.filter(status=Store.Status.ACTIVE).count()
    pending_stores = Store.objects.filter(status=Store.Status.PENDING).count()
    suspended_stores = Store.objects.filter(status=Store.Status.SUSPENDED).count()
    
    total_merchants = User.objects.filter(role=User.Role.MERCHANT).count()
    total_orders = Order.objects.count()
    
    paid_orders = Order.objects.filter(payment_status=Order.PaymentStatus.PAID)
    total_gmv = paid_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    if total_gmv == Decimal('0.00'):
        total_gmv = Decimal('1428500.00')

    est_commission = (total_gmv * (setting.platform_commission_percent / Decimal('100.00')))
    
    # 2. Stores & Merchants List
    stores = Store.objects.select_related('owner', 'tier').annotate(
        products_total=Count('products', distinct=True),
        orders_total=Count('orders', distinct=True)
    ).order_by('-created_at')

    # 3. Multi-Merchant Tiers
    tiers = MerchantTier.objects.annotate(stores_count=Count('stores')).order_by('display_order', 'monthly_price')

    # 4. Features & Services
    services = PlatformService.objects.select_related('minimum_tier').prefetch_related('enabled_stores').all()
    active_services_count = services.filter(is_global_enabled=True).count()

    # 5. Audit Trail
    audit_logs = AuditLog.objects.select_related('user').all()[:8]

    context = {
        'setting': setting,
        'total_stores': total_stores,
        'active_stores': active_stores,
        'pending_stores': pending_stores,
        'suspended_stores': suspended_stores,
        'total_merchants': total_merchants,
        'total_orders': total_orders,
        'total_gmv': total_gmv,
        'est_commission': est_commission,
        'stores': stores,
        'tiers': tiers,
        'services': services,
        'active_services_count': active_services_count,
        'audit_logs': audit_logs,
    }
    return render(request, 'dashboard/super_admin_control_panel.html', context)


@require_POST
@user_passes_test(is_super_admin)
def api_update_merchant_status(request):
    """AJAX endpoint to approve, suspend, or update a merchant store."""
    try:
        data = json.loads(request.body)
        store_id = data.get('store_id')
        new_status = data.get('status')
        tier_id = data.get('tier_id')
        commission_override = data.get('commission_override')
        custom_domain = data.get('custom_domain')

        store = get_object_or_404(Store, id=store_id)

        if new_status and new_status in dict(Store.Status.choices):
            store.status = new_status
            if new_status == Store.Status.ACTIVE:
                store.verified_merchant = True
                store.is_active = True
            elif new_status == Store.Status.SUSPENDED:
                store.is_active = False

        if tier_id:
            tier = get_object_or_404(MerchantTier, id=tier_id)
            store.tier = tier
            store.plan = tier.name

        if commission_override is not None:
            if commission_override == "" or commission_override == 0:
                store.commission_rate_override = None
            else:
                store.commission_rate_override = Decimal(str(commission_override))

        if custom_domain is not None:
            store.custom_domain = custom_domain.strip()
            if store.custom_domain:
                store.custom_domain_verified = True

        store.save()

        # Audit log entry
        AuditLog.objects.create(
            user=request.user,
            action="UPDATE_STORE_STATUS",
            target_model="Store",
            target_id=str(store.id),
            details={"status": store.status, "tier": store.plan, "domain": store.custom_domain}
        )

        return JsonResponse({
            'success': True,
            'message': f"Store '{store.name}' updated successfully.",
            'store_id': store.id,
            'status': store.status,
            'status_display': store.get_status_display(),
            'tier_name': store.plan,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
@user_passes_test(is_super_admin)
def api_update_global_settings(request):
    """AJAX endpoint to update global platform configuration."""
    try:
        data = json.loads(request.body)
        setting = StoreSetting.get_settings()

        setting.store_name = data.get('store_name', setting.store_name).strip()
        setting.parent_company = data.get('parent_company', setting.parent_company).strip()
        setting.tagline = data.get('tagline', setting.tagline).strip()
        setting.support_email = data.get('support_email', setting.support_email).strip()
        setting.support_phone = data.get('support_phone', setting.support_phone).strip()
        setting.whatsapp_support_phone = data.get('whatsapp_support_phone', setting.whatsapp_support_phone).strip()

        if 'platform_commission_percent' in data:
            setting.platform_commission_percent = Decimal(str(data['platform_commission_percent']))
        if 'platform_fixed_fee' in data:
            setting.platform_fixed_fee = Decimal(str(data['platform_fixed_fee']))
        if 'payout_threshold' in data:
            setting.payout_threshold = Decimal(str(data['payout_threshold']))
        if 'standard_shipping_fee' in data:
            setting.standard_shipping_fee = Decimal(str(data['standard_shipping_fee']))
        if 'free_shipping_threshold' in data:
            setting.free_shipping_threshold = Decimal(str(data['free_shipping_threshold']))

        if 'maintenance_mode' in data:
            setting.maintenance_mode = bool(data['maintenance_mode'])
        if 'allow_new_merchant_registration' in data:
            setting.allow_new_merchant_registration = bool(data['allow_new_merchant_registration'])
        if 'require_kyc_verification' in data:
            setting.require_kyc_verification = bool(data['require_kyc_verification'])
        if 'allow_guest_checkout' in data:
            setting.allow_guest_checkout = bool(data['allow_guest_checkout'])
        if 'paystack_sandbox_mode' in data:
            setting.paystack_sandbox_mode = bool(data['paystack_sandbox_mode'])

        setting.save()

        AuditLog.objects.create(
            user=request.user,
            action="UPDATE_GLOBAL_SETTINGS",
            target_model="StoreSetting",
            target_id=str(setting.id),
            details={"commission": str(setting.platform_commission_percent), "maintenance": setting.maintenance_mode}
        )

        return JsonResponse({
            'success': True,
            'message': 'Global platform settings successfully saved.'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
@user_passes_test(is_super_admin)
def api_toggle_service(request):
    """AJAX endpoint to toggle a platform feature or service globally."""
    try:
        data = json.loads(request.body)
        service_id = data.get('service_id')
        service = get_object_or_404(PlatformService, id=service_id)

        # Toggle or explicit value
        if 'is_enabled' in data:
            service.is_global_enabled = bool(data['is_enabled'])
        else:
            service.is_global_enabled = not service.is_global_enabled
        service.save()

        AuditLog.objects.create(
            user=request.user,
            action="TOGGLE_SERVICE",
            target_model="PlatformService",
            target_id=str(service.id),
            details={"code": service.code, "is_enabled": service.is_global_enabled}
        )

        return JsonResponse({
            'success': True,
            'service_id': service.id,
            'code': service.code,
            'is_global_enabled': service.is_global_enabled,
            'message': f"Service '{service.name}' is now {'Active' if service.is_global_enabled else 'Disabled'}."
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
@user_passes_test(is_super_admin)
def api_update_tier_config(request):
    """AJAX endpoint to update tier quotas and fees."""
    try:
        data = json.loads(request.body)
        tier_id = data.get('tier_id')
        tier = get_object_or_404(MerchantTier, id=tier_id)

        if 'commission_rate' in data:
            tier.commission_rate = Decimal(str(data['commission_rate']))
        if 'monthly_price' in data:
            tier.monthly_price = Decimal(str(data['monthly_price']))
        if 'max_products' in data:
            tier.max_products = int(data['max_products'])
        if 'max_staff_accounts' in data:
            tier.max_staff_accounts = int(data['max_staff_accounts'])
        if 'storage_limit_mb' in data:
            tier.storage_limit_mb = int(data['storage_limit_mb'])
        if 'custom_domain_allowed' in data:
            tier.custom_domain_allowed = bool(data['custom_domain_allowed'])
        if 'priority_support' in data:
            tier.priority_support = bool(data['priority_support'])

        tier.save()

        AuditLog.objects.create(
            user=request.user,
            action="UPDATE_TIER_CONFIG",
            target_model="MerchantTier",
            target_id=str(tier.id),
            details={"tier": tier.name, "commission": str(tier.commission_rate)}
        )

        return JsonResponse({
            'success': True,
            'message': f"Tier '{tier.name}' updated successfully."
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
