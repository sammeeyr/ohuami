import pytest
from decimal import Decimal
from django.urls import reverse
from apps.catalog.models import Product


@pytest.mark.django_db
def test_product_listing(client, sample_product):
    response = client.get(reverse('catalog:list'))
    assert response.status_code == 200
    assert 'products' in response.context
    assert response.context['products'].count() >= 1


@pytest.mark.django_db
def test_product_detail(client, sample_product):
    response = client.get(reverse('catalog:product_detail', kwargs={'slug': sample_product.slug}))
    assert response.status_code == 200
    assert response.context['product'] == sample_product
    assert 'display-price' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_catalog_search(client, sample_product):
    response = client.get(reverse('catalog:search'), {'q': 'Smartphone'})
    assert response.status_code == 200
    assert 'Ultra 5G' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_price_discount_calculation(sample_category):
    product = Product.objects.create(
        name="Discount Test Phone",
        slug="discount-test-phone",
        category=sample_category,
        base_price=Decimal("80000.00"),
        comparison_price=Decimal("100000.00"),
        sku="TEST-DISC-01",
        stock_quantity=10,
        is_active=True
    )
    assert product.discount_percentage == 20
    assert product.amount_saved == Decimal("20000.00")
