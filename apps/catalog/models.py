import secrets
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class MerchantTier(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    monthly_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    annual_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5.00'), help_text="Platform commission % on sales")
    max_products = models.PositiveIntegerField(default=50, help_text="Maximum products allowed")
    max_staff_accounts = models.PositiveIntegerField(default=2, help_text="Staff users limit")
    storage_limit_mb = models.PositiveIntegerField(default=1024, help_text="Storage limit in MB")
    custom_domain_allowed = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    analytics_tier = models.CharField(
        max_length=20, 
        choices=[('basic', 'Basic'), ('advanced', 'Advanced'), ('enterprise', 'Enterprise')], 
        default='basic'
    )
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Merchant Tier')
        verbose_name_plural = _('Merchant Tiers')
        ordering = ['display_order', 'monthly_price']

    def __str__(self):
        return f"{self.name} (₦{self.monthly_price}/mo - {self.commission_rate}%)"


class Store(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        PENDING = 'pending', _('Pending Verification')
        SUSPENDED = 'suspended', _('Suspended')
        ARCHIVED = 'archived', _('Archived')

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stores')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True)
    tagline = models.CharField(max_length=200, blank=True, default="Style that speaks you. Trendy. Classy. Affordable.")
    description = models.TextField(blank=True, default="Discover the latest fashion, accessories and lifestyle essentials — all in one place.")
    tier = models.ForeignKey(MerchantTier, on_delete=models.SET_NULL, null=True, blank=True, related_name='stores')
    plan = models.CharField(max_length=50, default='Pro Plan')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    logo = models.ImageField(upload_to='stores/logos/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='stores/banners/', blank=True, null=True)
    followers_count = models.PositiveIntegerField(default=142)
    is_active = models.BooleanField(default=True)

    # Multi-Merchant Routing & Custom Domains
    subdomain = models.CharField(max_length=100, blank=True, default='')
    custom_domain = models.CharField(max_length=255, blank=True, default='', help_text="e.g. storename.com or sunshinefashion.ng")
    custom_domain_verified = models.BooleanField(default=False)

    # Financial & Payout Settings
    commission_rate_override = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Custom commission % if overriding tier default")
    bank_name = models.CharField(max_length=100, blank=True, default='Zenith Bank')
    bank_account_number = models.CharField(max_length=20, blank=True, default='1023456789')
    bank_account_name = models.CharField(max_length=150, blank=True, default='Sunshine Fashion Enterprises')
    payout_schedule = models.CharField(
        max_length=20,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        default='weekly'
    )
    bvn_verified = models.BooleanField(default=True)

    # Resource Limits & KYC
    storage_quota_mb = models.PositiveIntegerField(default=1024)
    max_products_limit = models.PositiveIntegerField(default=500)
    verified_merchant = models.BooleanField(default=True)
    verification_notes = models.TextField(blank=True, default='')

    # CORS & Headless API Configuration
    cors_allowed_origins = models.TextField(
        blank=True,
        default="http://localhost:3000, http://127.0.0.1:3000, http://localhost:8000",
        help_text="Comma-separated allowed origins for cross-origin resource sharing (CORS)"
    )
    api_key = models.CharField(max_length=64, blank=True, default='', db_index=True, help_text="Secret API key for headless store integration")
    api_key_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Store')
        verbose_name_plural = _('Stores')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.owner.email})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.subdomain:
            self.subdomain = self.slug
        if not self.api_key:
            self.api_key = f"ohu_{secrets.token_hex(24)}"
        super().save(*args, **kwargs)

    def regenerate_api_key(self):
        self.api_key = f"ohu_{secrets.token_hex(24)}"
        self.save(update_fields=['api_key'])
        return self.api_key

    def get_cors_origins_list(self):
        if not self.cors_allowed_origins:
            return []
        return [origin.strip() for origin in self.cors_allowed_origins.split(',') if origin.strip()]

    def get_absolute_url(self):
        return reverse('catalog:storefront', kwargs={'store_slug': self.slug})

    @property
    def effective_commission_rate(self):
        if self.commission_rate_override is not None:
            return self.commission_rate_override
        if self.tier:
            return self.tier.commission_rate
        return Decimal('5.00')

    @property
    def effective_max_products(self):
        if self.max_products_limit:
            return self.max_products_limit
        if self.tier:
            return self.tier.max_products
        return 500


class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(blank=True, default='')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, default='', help_text="Icon identifier e.g. phone, dress, bag, shoe")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})


class Brand(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=180, unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    description = models.TextField()
    specifications = models.JSONField(default=dict, blank=True, help_text="Structured specs map")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    seller_name = models.CharField(max_length=150, default='Sunshine Fashion')
    
    # Financial fields
    base_price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Current selling price in NGN")
    comparison_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Crossed-out original price")
    
    sku = models.CharField(max_length=100, unique=True)
    stock_quantity = models.PositiveIntegerField(default=10, help_text="Direct product stock if no variants")
    
    # Flags & Discovery
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_flash_sale = models.BooleanField(default=False)
    badge_text = models.CharField(max_length=50, blank=True, default='', help_text="Custom badge like '-20%', 'Hot Deal', etc.")
    
    # SEO
    seo_title = models.CharField(max_length=200, blank=True, default='')
    seo_description = models.TextField(blank=True, default='')
    
    # Reassurance and verified guarantees
    is_verified_seller = models.BooleanField(default=True)
    is_quality_checked = models.BooleanField(default=True)
    fast_dispatch = models.BooleanField(default=True)
    protected_checkout = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-is_featured', '-is_trending', '-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})

    @property
    def discount_percentage(self):
        if self.comparison_price and self.comparison_price > self.base_price:
            diff = self.comparison_price - self.base_price
            return int(round((diff / self.comparison_price) * 100))
        return 0

    @property
    def amount_saved(self):
        if self.comparison_price and self.comparison_price > self.base_price:
            return self.comparison_price - self.base_price
        return Decimal('0.00')

    @property
    def primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        if not primary:
            primary = self.images.first()
        return primary

    @property
    def available_stock(self):
        if self.variants.exists():
            return sum(v.stock_quantity for v in self.variants.filter(is_active=True))
        return self.stock_quantity

    @property
    def is_in_stock(self):
        return self.available_stock > 0

    @property
    def rating_average(self):
        reviews = self.reviews.filter(is_moderated=True)
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            return round(avg, 1) if avg else 5.0
        return 5.0

    @property
    def rating_count(self):
        count = self.reviews.filter(is_moderated=True).count()
        return count if count > 0 else 24


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True, default='')
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['-is_primary', 'display_order', 'id']

    def __str__(self):
        return f"Image for {self.product.name} ({self.id})"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductAttribute(models.Model):
    name = models.CharField(max_length=100, help_text="e.g. Color, Size, Storage")
    code = models.SlugField(max_length=100, unique=True, help_text="e.g. color, size")

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100, help_text="e.g. Red, Black, S, M, L")
    color_hex = models.CharField(max_length=20, blank=True, default='', help_text="Hex color swatch e.g. #E53935")
    image = models.ImageField(upload_to='attributes/', blank=True, null=True)

    class Meta:
        unique_together = ('attribute', 'value')

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=255, help_text="e.g. Size: M, Color: Red")
    sku = models.CharField(max_length=100, unique=True)
    attribute_values = models.ManyToManyField(ProductAttributeValue, related_name='variants')
    price_override = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=10)
    image = models.ForeignKey(ProductImage, on_delete=models.SET_NULL, null=True, blank=True, related_name='variant_images')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Product Variant')
        verbose_name_plural = _('Product Variants')

    def __str__(self):
        return f"{self.product.name} - {self.name} ({self.sku})"

    @property
    def price(self):
        return self.price_override if self.price_override is not None else self.product.base_price

    @property
    def comparison_price(self):
        return self.product.comparison_price

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0
