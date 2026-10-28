import pytest
from decimal import Decimal
from apps.catalog.models import Category, Brand, Product, ProductVariant
from apps.accounts.models import User, Address


@pytest.fixture
def sample_category(db):
    return Category.objects.create(name="Laptops", slug="laptops", display_order=1)


@pytest.fixture
def sample_brand(db):
    return Brand.objects.create(name="Cube Tech Pro", slug="cube-tech-pro")


@pytest.fixture
def sample_product(db, sample_category, sample_brand):
    product = Product.objects.create(
        name="Cube Pro 16 Ultra 5G Smartphone",
        slug="cube-pro-16-ultra-5g-smartphone",
        category=sample_category,
        brand=sample_brand,
        seller_name="Cube Tech Official Store",
        base_price=Decimal("850000.00"),
        comparison_price=Decimal("1180000.00"),
        sku="CT-P16U-001",
        stock_quantity=20,
        is_active=True,
        is_featured=True,
        is_flash_sale=True,
        is_trending=True,
        specifications={"RAM": "16GB", "Display": "6.8 inch AMOLED"}
    )
    ProductVariant.objects.create(
        product=product,
        name="Titanium Black / 256GB",
        sku="CT-P16U-001-256",
        price_override=Decimal("850000.00"),
        stock_quantity=15,
        is_active=True
    )
    return product


@pytest.fixture
def sample_customer(db):
    user = User.objects.create_user(email="customer@example.com", password="Password123!", phone="08012345678")
    Address.objects.create(
        user=user,
        recipient_name="John Doe",
        phone="08012345678",
        street_address="12 Main Street",
        city="Abuja",
        state="FCT Abuja",
        country="Nigeria",
        is_default=True
    )
    return user
