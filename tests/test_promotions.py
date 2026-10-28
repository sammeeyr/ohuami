import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from apps.promotions.models import Coupon


@pytest.mark.django_db
def test_percentage_coupon_calculation():
    coupon = Coupon.objects.create(
        code="TEST20",
        discount_type=Coupon.DiscountType.PERCENTAGE,
        discount_value=Decimal("20.00"),
        min_order_value=Decimal("10000.00"),
        is_active=True
    )
    # Order of 50,000 -> 20% is 10,000
    subtotal = Decimal("50000.00")
    is_valid, _ = coupon.is_valid(subtotal)
    assert is_valid is True
    assert coupon.calculate_discount(subtotal) == Decimal("10000.00")


@pytest.mark.django_db
def test_fixed_coupon_calculation():
    coupon = Coupon.objects.create(
        code="FIXED5000",
        discount_type=Coupon.DiscountType.FIXED,
        discount_value=Decimal("5000.00"),
        min_order_value=Decimal("10000.00"),
        is_active=True
    )
    subtotal = Decimal("20000.00")
    assert coupon.calculate_discount(subtotal) == Decimal("5000.00")


@pytest.mark.django_db
def test_coupon_min_order_enforcement():
    coupon = Coupon.objects.create(
        code="MIN50K",
        discount_type=Coupon.DiscountType.PERCENTAGE,
        discount_value=Decimal("10.00"),
        min_order_value=Decimal("50000.00"),
        is_active=True
    )
    is_valid, msg = coupon.is_valid(Decimal("30000.00"))
    assert is_valid is False
    assert "Minimum order amount" in msg


@pytest.mark.django_db
def test_expired_coupon_rejection():
    yesterday = timezone.now() - timedelta(days=1)
    coupon = Coupon.objects.create(
        code="EXPIRED",
        discount_type=Coupon.DiscountType.PERCENTAGE,
        discount_value=Decimal("15.00"),
        end_date=yesterday,
        is_active=True
    )
    is_valid, msg = coupon.is_valid(Decimal("100000.00"))
    assert is_valid is False
    assert "expired" in msg.lower()
