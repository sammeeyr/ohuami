import json
import pytest
from decimal import Decimal
from django.urls import reverse
from apps.accounts.models import User
from apps.catalog.models import Store, MerchantTier
from apps.core.models import StoreSetting, PlatformService, AuditLog


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        email="superadmin@ohuami.com",
        password="SuperPassword123!",
        first_name="Super",
        last_name="Admin",
        role=User.Role.ADMIN,
    )


@pytest.fixture
def regular_customer(db):
    return User.objects.create_user(
        email="customer_shopper@example.com",
        password="CustomerPassword123!",
        role=User.Role.CUSTOMER,
    )


@pytest.fixture
def merchant_tier(db):
    return MerchantTier.objects.create(
        name="Pro Scale",
        slug="pro-scale",
        monthly_price=Decimal("35000.00"),
        commission_rate=Decimal("3.50"),
        max_products=1000,
        max_staff_accounts=10,
        storage_limit_mb=10240,
        custom_domain_allowed=True,
    )


@pytest.fixture
def sample_merchant_store(db, regular_customer, merchant_tier):
    return Store.objects.create(
        name="Apex Gadgets",
        slug="apex-gadgets",
        owner=regular_customer,
        tier=merchant_tier,
        status=Store.Status.PENDING,
        bank_name="Access Bank",
        bank_account_number="0123456789",
        bank_account_name="Apex Gadgets Ltd",
    )


@pytest.fixture
def sample_service(db):
    return PlatformService.objects.create(
        name="WhatsApp Conversational Commerce",
        code="whatsapp_commerce",
        category="Omnichannel",
        description="Automated catalog sharing and checkout via WhatsApp Business API",
        is_global_enabled=True,
    )


@pytest.mark.django_db
def test_super_admin_control_panel_access_control(client, superuser, regular_customer):
    """Anonymous and regular customers should not be able to access the super admin control center."""
    url = reverse('dashboard:super_admin_control_panel')
    
    # 1. Anonymous access redirects to login
    response = client.get(url)
    assert response.status_code == 302
    assert '/accounts/login/' in response.url

    # 2. Regular customer receives 403 Forbidden
    client.force_login(regular_customer)
    response = client.get(url)
    assert response.status_code == 403

    # 3. Superuser gets 200 OK with full control panel
    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200
    assert "Super Admin Control Center" in response.content.decode()
    assert "OHUAMI" in response.content.decode()
    assert "Cube Tech Enterprises" in response.content.decode()


@pytest.mark.django_db
def test_api_update_merchant_status(client, superuser, sample_merchant_store, merchant_tier):
    """Super admin can approve, suspend, or update merchant status, tier, and commission override."""
    client.force_login(superuser)
    url = reverse('dashboard:api_update_merchant_status')

    payload = {
        'store_id': sample_merchant_store.id,
        'status': Store.Status.ACTIVE,
        'tier_id': merchant_tier.id,
        'commission_rate_override': '2.75',
        'bvn_verified': True,
        'verified_merchant': True,
        'verification_notes': 'Verified CAC and Corporate BVN credentials',
    }

    response = client.post(
        url,
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert data['store']['status'] == Store.Status.ACTIVE

    # Verify database persistence
    sample_merchant_store.refresh_from_db()
    assert sample_merchant_store.status == Store.Status.ACTIVE
    assert sample_merchant_store.bvn_verified is True
    assert sample_merchant_store.verified_merchant is True
    assert sample_merchant_store.commission_rate_override == Decimal('2.75')
    assert sample_merchant_store.verification_notes == 'Verified CAC and Corporate BVN credentials'

    # Verify audit log entry was created
    audit = AuditLog.objects.filter(action="UPDATE_MERCHANT_STATUS", user=superuser).first()
    assert audit is not None
    assert "Apex Gadgets" in audit.details


@pytest.mark.django_db
def test_api_update_global_settings(client, superuser):
    """Super admin can update global platform settings like commission, shipping fee, maintenance mode."""
    client.force_login(superuser)
    url = reverse('dashboard:api_update_global_settings')

    payload = {
        'store_name': 'OHUAMI Multi-Vendor',
        'parent_company': 'Cube Tech Enterprises Group',
        'platform_commission_percent': '4.50',
        'platform_fixed_fee': '150.00',
        'standard_shipping_fee': '2500.00',
        'free_shipping_threshold': '60000.00',
        'maintenance_mode': False,
        'allow_new_merchant_registration': True,
        'require_kyc_verification': True,
    }

    response = client.post(
        url,
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True

    # Check database persistence in singleton
    setting = StoreSetting.get_settings()
    assert setting.store_name == 'OHUAMI Multi-Vendor'
    assert setting.parent_company == 'Cube Tech Enterprises Group'
    assert setting.platform_commission_percent == Decimal('4.50')
    assert setting.standard_shipping_fee == Decimal('2500.00')
    assert setting.free_shipping_threshold == Decimal('60000.00')

    # Audit log check
    audit = AuditLog.objects.filter(action="UPDATE_GLOBAL_SETTINGS").first()
    assert audit is not None


@pytest.mark.django_db
def test_api_toggle_platform_service(client, superuser, sample_service):
    """Super admin can toggle platform services on/off with instant persistence."""
    client.force_login(superuser)
    url = reverse('dashboard:api_toggle_service')

    assert sample_service.is_global_enabled is True

    # Disable service
    response = client.post(
        url,
        data=json.dumps({'code': sample_service.code, 'is_global_enabled': False}),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.json()['is_global_enabled'] is False

    sample_service.refresh_from_db()
    assert sample_service.is_global_enabled is False

    # Re-enable service
    response = client.post(
        url,
        data=json.dumps({'code': sample_service.code, 'is_global_enabled': True}),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.json()['is_global_enabled'] is True

    sample_service.refresh_from_db()
    assert sample_service.is_global_enabled is True


@pytest.mark.django_db
def test_api_update_tier_config(client, superuser, merchant_tier):
    """Super admin can modify tier fees, quotas, and limits."""
    client.force_login(superuser)
    url = reverse('dashboard:api_update_tier_config')

    payload = {
        'tier_id': merchant_tier.id,
        'monthly_price': '42000.00',
        'commission_rate': '3.20',
        'max_products': 2500,
        'max_staff_accounts': 15,
        'storage_limit_mb': 20480,
        'custom_domain_allowed': True,
        'priority_support': True,
    }

    response = client.post(
        url,
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.json()['success'] is True

    merchant_tier.refresh_from_db()
    assert merchant_tier.monthly_price == Decimal('42000.00')
    assert merchant_tier.commission_rate == Decimal('3.20')
    assert merchant_tier.max_products == 2500
    assert merchant_tier.max_staff_accounts == 15
    assert merchant_tier.priority_support is True


@pytest.mark.django_db
def test_django_admin_index_with_ohuami_branding(client, superuser, sample_merchant_store):
    """Django Admin index renders the OHUAMI Super Admin Hero banner and KPI cards."""
    client.force_login(superuser)
    response = client.get('/admin/')
    assert response.status_code == 200
    content = response.content.decode()
    assert "OHUAMI Control Panel" in content
    assert "CUBE TECH ENTERPRISES" in content
    assert "Open Super Admin Control Center" in content
    assert "Stores &amp; Merchants" in content or "Stores & Merchants" in content
    assert "Platform Commission" in content
