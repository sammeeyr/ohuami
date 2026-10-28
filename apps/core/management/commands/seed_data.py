from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User, Address
from apps.catalog.models import Store, MerchantTier, Category, Brand, Product, ProductImage, ProductAttribute, ProductAttributeValue, ProductVariant
from apps.orders.models import Order, OrderItem
from apps.promotions.models import Campaign, Coupon
from apps.reviews.models import Review
from apps.core.models import StoreSetting, PlatformService


class Command(BaseCommand):
    help = "Seeds database with official OHUAMI multi-tenant commerce catalog, stores, and test data."

    def handle(self, *args, **options):
        self.stdout.write("Seeding OHUAMI platform data...")

        # 1. Store Settings (Global branding & platform controls)
        setting = StoreSetting.get_settings()
        setting.store_name = "OHUAMI"
        setting.parent_company = "Cube Tech Enterprises"
        setting.tagline = "Your market. Your business. Your growth."
        setting.secondary_tagline = "Commerce made for your ambition."
        setting.support_email = "support@ohuami.com"
        setting.support_phone = "+234 800 2823 8324"
        setting.whatsapp_support_phone = "+234 801 234 5678"
        setting.standard_shipping_fee = Decimal('2000.00')
        setting.free_shipping_threshold = Decimal('100000.00')
        setting.platform_commission_percent = Decimal('5.00')
        setting.platform_fixed_fee = Decimal('100.00')
        setting.payout_threshold = Decimal('10000.00')
        setting.supported_currencies = ["NGN", "USD", "GBP", "GHS", "KES"]
        setting.allow_new_merchant_registration = True
        setting.require_kyc_verification = True
        setting.allow_guest_checkout = True
        setting.save()

        # 1.5 Merchant Tiers (Multi-Merchant Config)
        tier_free, _ = MerchantTier.objects.get_or_create(
            slug="free",
            defaults={
                "name": "Free Tier",
                "monthly_price": Decimal("0.00"),
                "annual_price": Decimal("0.00"),
                "commission_rate": Decimal("7.00"),
                "max_products": 15,
                "max_staff_accounts": 1,
                "storage_limit_mb": 250,
                "custom_domain_allowed": False,
                "priority_support": False,
                "analytics_tier": "basic",
                "display_order": 1,
                "description": "Essential tools for individual sellers and makers starting their digital market."
            }
        )

        tier_starter, _ = MerchantTier.objects.get_or_create(
            slug="starter",
            defaults={
                "name": "Starter Plan",
                "monthly_price": Decimal("15000.00"),
                "annual_price": Decimal("150000.00"),
                "commission_rate": Decimal("5.00"),
                "max_products": 75,
                "max_staff_accounts": 3,
                "storage_limit_mb": 1024,
                "custom_domain_allowed": True,
                "priority_support": False,
                "analytics_tier": "basic",
                "display_order": 2,
                "description": "For growing boutique stores seeking branded subdomains and multiple staff seats."
            }
        )

        tier_pro, _ = MerchantTier.objects.get_or_create(
            slug="pro",
            defaults={
                "name": "Pro Plan",
                "monthly_price": Decimal("35000.00"),
                "annual_price": Decimal("350000.00"),
                "commission_rate": Decimal("3.50"),
                "max_products": 500,
                "max_staff_accounts": 10,
                "storage_limit_mb": 5120,
                "custom_domain_allowed": True,
                "priority_support": True,
                "analytics_tier": "advanced",
                "display_order": 3,
                "description": "Full-featured omnichannel platform with lower commissions, high limits, and priority support."
            }
        )

        tier_enterprise, _ = MerchantTier.objects.get_or_create(
            slug="enterprise",
            defaults={
                "name": "Enterprise Custom",
                "monthly_price": Decimal("85000.00"),
                "annual_price": Decimal("850000.00"),
                "commission_rate": Decimal("2.00"),
                "max_products": 5000,
                "max_staff_accounts": 50,
                "storage_limit_mb": 25600,
                "custom_domain_allowed": True,
                "priority_support": True,
                "analytics_tier": "enterprise",
                "display_order": 4,
                "description": "Dedicated cloud infrastructure, custom ERP integrations, and lowest transaction fees."
            }
        )

        # 1.6 Platform Features & Services
        services_data = [
            {
                "code": "ai_automation",
                "name": "AI Catalog & Description Assistant",
                "category": PlatformService.Category.AI,
                "icon": "sparkle",
                "is_premium": False,
                "minimum_tier": tier_starter,
                "description": "Generates SEO-rich product descriptions, auto-tags, and category recommendations via AI."
            },
            {
                "code": "whatsapp_commerce",
                "name": "WhatsApp Direct Commerce",
                "category": PlatformService.Category.CHANNELS,
                "icon": "chat",
                "is_premium": False,
                "minimum_tier": tier_free,
                "description": "Instant 1-click cart order submission, receipt delivery, and live customer chat over WhatsApp."
            },
            {
                "code": "custom_domains",
                "name": "Custom Domain & Automated SSL",
                "category": PlatformService.Category.CHANNELS,
                "icon": "globe",
                "is_premium": True,
                "minimum_tier": tier_starter,
                "description": "Allows merchants to link their own registered domains (e.g. yourbrand.ng) with auto-renewing SSL."
            },
            {
                "code": "pos_terminal",
                "name": "Point of Sale (POS) Offline Sync",
                "category": PlatformService.Category.CHANNELS,
                "icon": "desktop",
                "is_premium": True,
                "minimum_tier": tier_pro,
                "description": "Unified physical retail counter checkout with receipt printing and multi-location inventory deduction."
            },
            {
                "code": "multi_currency",
                "name": "Multi-Currency Dynamic Conversion",
                "category": PlatformService.Category.PAYMENTS,
                "icon": "currency",
                "is_premium": False,
                "minimum_tier": tier_pro,
                "description": "Accept USD, GBP, GHS, and KES with automated FX hedging and settlement in Nigerian Naira."
            },
            {
                "code": "escrow_protection",
                "name": "Buyer Delivery Escrow Guarantee",
                "category": PlatformService.Category.PAYMENTS,
                "icon": "shield",
                "is_premium": False,
                "minimum_tier": tier_free,
                "description": "Protects buyers with automatic 72-hour payout release upon delivery confirmation."
            },
            {
                "code": "automated_logistics",
                "name": "Express Logistics Dispatch API",
                "category": PlatformService.Category.LOGISTICS,
                "icon": "truck",
                "is_premium": False,
                "minimum_tier": tier_free,
                "description": "Instant waybill generation and automatic courier dispatch with Sendbox, GIG, and DHL."
            },
            {
                "code": "advanced_analytics",
                "name": "Cohort Retention & Predictive Analytics",
                "category": PlatformService.Category.GROWTH,
                "icon": "chart",
                "is_premium": True,
                "minimum_tier": tier_pro,
                "description": "Customer lifetime value, repurchase frequencies, and predictive stockout alerts."
            },
            {
                "code": "abandoned_cart_recovery",
                "name": "Automated Cart Recovery Sequences",
                "category": PlatformService.Category.GROWTH,
                "icon": "bell",
                "is_premium": False,
                "minimum_tier": tier_starter,
                "description": "Automated SMS and email reminders with dynamic single-use discount coupon links."
            },
        ]

        for s_data in services_data:
            PlatformService.objects.get_or_create(
                code=s_data["code"],
                defaults={
                    "name": s_data["name"],
                    "category": s_data["category"],
                    "icon": s_data["icon"],
                    "is_premium": s_data["is_premium"],
                    "minimum_tier": s_data["minimum_tier"],
                    "description": s_data["description"],
                    "is_global_enabled": True
                }
            )

        # 2. Users
        admin_user, _ = User.objects.get_or_create(
            email="admin@ohuami.com",
            defaults={
                "first_name": "Admin",
                "last_name": "OHUAMI",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            }
        )
        admin_user.set_password("Admin@123456")
        admin_user.save()

        merchant_user, _ = User.objects.get_or_create(
            email="chinedu@example.com",
            defaults={
                "first_name": "Chinedu",
                "last_name": "Okafor",
                "phone": "+234 801 234 5678",
                "role": User.Role.MERCHANT,
                "is_staff": True,
                "is_verified": True,
            }
        )
        merchant_user.first_name = "Chinedu"
        merchant_user.last_name = "Okafor"
        merchant_user.phone = "+234 801 234 5678"
        merchant_user.role = User.Role.MERCHANT
        merchant_user.set_password("Password@123")
        merchant_user.save()

        Address.objects.update_or_create(
            user=merchant_user,
            is_default=True,
            defaults={
                "recipient_name": "Chinedu Okafor",
                "phone": "+234 801 234 5678",
                "street_address": "128, Ganiyu Street, GRA",
                "city": "Abuja",
                "state": "FCT",
                "country": "Nigeria",
            }
        )

        customer_user, _ = User.objects.get_or_create(
            email="customer@example.com",
            defaults={
                "first_name": "Amina",
                "last_name": "Bello",
                "phone": "+234 802 345 6789",
                "role": User.Role.CUSTOMER,
                "is_verified": True,
            }
        )
        customer_user.set_password("Customer@123")
        customer_user.save()

        # 3. Stores (Multi-Merchant Tenants)
        store_sunshine, _ = Store.objects.get_or_create(
            slug="sunshine-fashion",
            defaults={
                "owner": merchant_user,
                "name": "Sunshine Fashion",
                "tagline": "Style that speaks you. Trendy. Classy. Affordable.",
                "description": "Discover the latest fashion, accessories and lifestyle essentials — all in one place.",
                "plan": "Pro Plan",
                "tier": tier_pro,
                "status": Store.Status.ACTIVE,
                "followers_count": 1248,
                "is_active": True,
                "bank_name": "Zenith Bank",
                "bank_account_number": "1023456789",
                "bank_account_name": "Sunshine Fashion Ent.",
                "bvn_verified": True,
                "subdomain": "sunshine-fashion",
                "custom_domain": "sunshinefashion.ng",
                "custom_domain_verified": True,
                "verified_merchant": True,
            }
        )
        store_sunshine.owner = merchant_user
        store_sunshine.tier = tier_pro
        store_sunshine.status = Store.Status.ACTIVE
        store_sunshine.followers_count = 1248
        store_sunshine.save()

        # Merchant 2: Halima Danjuma (Savannah Organics)
        merchant_halima, _ = User.objects.get_or_create(
            email="halima@example.com",
            defaults={
                "first_name": "Halima",
                "last_name": "Danjuma",
                "phone": "+234 803 987 6543",
                "role": User.Role.MERCHANT,
                "is_verified": True,
            }
        )
        merchant_halima.set_password("Password@123")
        merchant_halima.save()

        store_savannah, _ = Store.objects.get_or_create(
            slug="savannah-organics",
            defaults={
                "owner": merchant_halima,
                "name": "Savannah Organics",
                "tagline": "Pure botanical beauty and organic wellness from Northern Nigeria.",
                "description": "Handcrafted shea butter, black soap, and botanical glow oils.",
                "plan": "Starter Plan",
                "tier": tier_starter,
                "status": Store.Status.ACTIVE,
                "followers_count": 640,
                "is_active": True,
                "bank_name": "Guaranty Trust Bank",
                "bank_account_number": "0123456789",
                "bank_account_name": "Savannah Organics Ventures",
                "bvn_verified": True,
                "subdomain": "savannah-organics",
                "verified_merchant": True,
            }
        )

        # Merchant 3: Tunde Balogun (Lagos Footwear Hub - Pending Verification)
        merchant_tunde, _ = User.objects.get_or_create(
            email="tunde@example.com",
            defaults={
                "first_name": "Tunde",
                "last_name": "Balogun",
                "phone": "+234 802 111 2233",
                "role": User.Role.MERCHANT,
                "is_verified": False,
            }
        )
        merchant_tunde.set_password("Password@123")
        merchant_tunde.save()

        store_tunde, _ = Store.objects.get_or_create(
            slug="lagos-footwear-hub",
            defaults={
                "owner": merchant_tunde,
                "name": "Lagos Footwear Hub",
                "tagline": "Handmade leather sandals, mules, and dress shoes crafted in Aba & Lagos.",
                "description": "Authentic Nigerian crafted leather footwear for men and women.",
                "plan": "Free Tier",
                "tier": tier_free,
                "status": Store.Status.PENDING,
                "followers_count": 85,
                "is_active": True,
                "bank_name": "Access Bank",
                "bank_account_number": "0987654321",
                "bank_account_name": "Tunde Balogun Trades",
                "bvn_verified": False,
                "subdomain": "lagos-footwear",
                "verified_merchant": False,
                "verification_notes": "Submitted business registration certificate. Awaiting phone KYC confirmation.",
            }
        )

        # 4. Categories (Matching Screen 3 circular navigation pills)
        cat_women, _ = Category.objects.get_or_create(name="Women", defaults={"slug": "women", "icon": "dress", "display_order": 1})
        cat_men, _ = Category.objects.get_or_create(name="Men", defaults={"slug": "men", "icon": "shirt", "display_order": 2})
        cat_bags, _ = Category.objects.get_or_create(name="Bags", defaults={"slug": "bags", "icon": "bag", "display_order": 3})
        cat_shoes, _ = Category.objects.get_or_create(name="Shoes", defaults={"slug": "shoes", "icon": "shoe", "display_order": 4})
        cat_accessories, _ = Category.objects.get_or_create(name="Accessories", defaults={"slug": "accessories", "icon": "glasses", "display_order": 5})
        cat_beauty, _ = Category.objects.get_or_create(name="Beauty", defaults={"slug": "beauty", "icon": "sparkle", "display_order": 6})

        # Also preserve electronics categories
        cat_phones, _ = Category.objects.get_or_create(name="Smartphones & Tablets", defaults={"slug": "smartphones", "display_order": 10})
        cat_laptops, _ = Category.objects.get_or_create(name="Laptops & Workstations", defaults={"slug": "laptops", "display_order": 11})

        # 5. Brands
        brand_sunshine, _ = Brand.objects.get_or_create(name="Sunshine Collection", defaults={"slug": "sunshine-collection"})
        brand_cubetech, _ = Brand.objects.get_or_create(name="Cube Tech Pro", defaults={"slug": "cube-tech-pro"})

        # 6. Attributes (Size, Color)
        attr_size, _ = ProductAttribute.objects.get_or_create(code="size", defaults={"name": "Size"})
        val_s, _ = ProductAttributeValue.objects.get_or_create(attribute=attr_size, value="S")
        val_m, _ = ProductAttributeValue.objects.get_or_create(attribute=attr_size, value="M")
        val_l, _ = ProductAttributeValue.objects.get_or_create(attribute=attr_size, value="L")
        val_xl, _ = ProductAttributeValue.objects.get_or_create(attribute=attr_size, value="XL")
        val_onesize, _ = ProductAttributeValue.objects.get_or_create(attribute=attr_size, value="One Size")
        val_size42, _ = ProductAttributeValue.objects.get_or_create(attribute=attr_size, value="42")

        attr_color, _ = ProductAttribute.objects.get_or_create(code="color", defaults={"name": "Color"})
        attr_color.name = "Color"
        attr_color.save()
        val_burgundy, _ = ProductAttributeValue.objects.get_or_create(attribute=attr_color, value="Burgundy", defaults={"color_hex": "#8B1E3F"})
        val_black, _ = ProductAttributeValue.objects.get_or_create(attribute=attr_color, value="Black", defaults={"color_hex": "#111111"})
        val_cream, _ = ProductAttributeValue.objects.get_or_create(attribute=attr_color, value="Cream", defaults={"color_hex": "#EFE8DC"})
        val_white, _ = ProductAttributeValue.objects.get_or_create(attribute=attr_color, value="White", defaults={"color_hex": "#FFFFFF"})

        # 7. Products (Matching UI Showcase Screens 3, 4, 5, 6)
        # Product 1: Elegant Midi Dress (Screen 4 Main Product)
        p1, _ = Product.objects.get_or_create(
            slug="elegant-midi-dress",
            defaults={
                "name": "Elegant Midi Dress",
                "store": store_sunshine,
                "category": cat_women,
                "brand": brand_sunshine,
                "seller_name": "Sunshine Fashion",
                "base_price": Decimal("28000.00"),
                "comparison_price": Decimal("35000.00"),
                "sku": "SF-DRS-001",
                "stock_quantity": 45,
                "is_active": True,
                "is_featured": True,
                "is_trending": True,
                "is_flash_sale": True,
                "badge_text": "-20%",
                "description": "A perfect blend of style and comfort. This elegant midi dress is designed for modern women who love simplicity with class. Made from high-grade stretch-crepe fabric that flatters every silhouette, suitable for formal events, dinners, or classy office wear.",
                "specifications": {
                    "Material": "Premium Stretch Crepe",
                    "Fit": "Tailored Slim Fit",
                    "Length": "Midi (Below Knee)",
                    "Neckline": "Deep V-Neck",
                    "Closure": "Concealed back zip",
                    "Care": "Machine wash cold or dry clean"
                }
            }
        )
        p1.store = store_sunshine
        p1.base_price = Decimal("28000.00")
        p1.comparison_price = Decimal("35000.00")
        p1.badge_text = "-20%"
        p1.save()

        # Product 1 Images
        ProductImage.objects.get_or_create(
            product=p1,
            image="products/elegant-midi-dress.png",
            defaults={"is_primary": True, "display_order": 1, "alt_text": "Elegant Midi Dress front view"}
        )
        ProductImage.objects.get_or_create(
            product=p1,
            image="products/elegant-midi-dress-1.png",
            defaults={"is_primary": False, "display_order": 2, "alt_text": "Elegant Midi Dress back detail"}
        )
        ProductImage.objects.get_or_create(
            product=p1,
            image="products/elegant-midi-dress-2.png",
            defaults={"is_primary": False, "display_order": 3, "alt_text": "Elegant Midi Dress side profile"}
        )
        ProductImage.objects.get_or_create(
            product=p1,
            image="products/elegant-midi-dress-3.png",
            defaults={"is_primary": False, "display_order": 4, "alt_text": "Elegant Midi Dress texture close-up"}
        )

        # Variants for Product 1 (S, M, L, XL with Burgundy, Black, Cream)
        v1_m, _ = ProductVariant.objects.get_or_create(
            product=p1,
            sku="SF-DRS-M-BUR",
            defaults={"name": "M / Burgundy", "stock_quantity": 15, "is_active": True}
        )
        v1_m.attribute_values.set([val_m, val_burgundy])

        v1_s, _ = ProductVariant.objects.get_or_create(
            product=p1,
            sku="SF-DRS-S-BUR",
            defaults={"name": "S / Burgundy", "stock_quantity": 10, "is_active": True}
        )
        v1_s.attribute_values.set([val_s, val_burgundy])

        v1_l, _ = ProductVariant.objects.get_or_create(
            product=p1,
            sku="SF-DRS-L-BLK",
            defaults={"name": "L / Black", "stock_quantity": 10, "is_active": True}
        )
        v1_l.attribute_values.set([val_l, val_black])

        v1_xl, _ = ProductVariant.objects.get_or_create(
            product=p1,
            sku="SF-DRS-XL-CRM",
            defaults={"name": "XL / Cream", "stock_quantity": 10, "is_active": True}
        )
        v1_xl.attribute_values.set([val_xl, val_cream])

        # Product 2: Classy Handbag (Screen 5 & 6)
        p2, _ = Product.objects.get_or_create(
            slug="classy-handbag",
            defaults={
                "name": "Classy Handbag",
                "store": store_sunshine,
                "category": cat_bags,
                "brand": brand_sunshine,
                "seller_name": "Sunshine Fashion",
                "base_price": Decimal("18500.00"),
                "comparison_price": Decimal("24000.00"),
                "sku": "SF-BAG-002",
                "stock_quantity": 30,
                "is_active": True,
                "is_featured": True,
                "is_trending": True,
                "badge_text": "Hot",
                "description": "Structured top-handle leather handbag featuring dual interior compartments, detachable adjustable shoulder strap, and gold-plated hardware. An absolute staple for work and weekend outings.",
                "specifications": {
                    "Material": "Vegan Saffiano Leather",
                    "Dimensions": "28cm x 20cm x 11cm",
                    "Hardware": "Gold Tone",
                    "Closure": "Magnetic Flap"
                }
            }
        )
        p2.store = store_sunshine
        p2.base_price = Decimal("18500.00")
        p2.save()

        ProductImage.objects.get_or_create(
            product=p2,
            image="products/classy-handbag.png",
            defaults={"is_primary": True, "display_order": 1, "alt_text": "Classy Handbag Black"}
        )

        v2, _ = ProductVariant.objects.get_or_create(
            product=p2,
            sku="SF-BAG-BLK",
            defaults={"name": "One Size / Black", "stock_quantity": 25, "is_active": True}
        )
        v2.attribute_values.set([val_onesize, val_black])

        # Product 3: White Sneakers (Screen 5 & 6)
        p3, _ = Product.objects.get_or_create(
            slug="white-sneakers",
            defaults={
                "name": "White Sneakers",
                "store": store_sunshine,
                "category": cat_shoes,
                "brand": brand_sunshine,
                "seller_name": "Sunshine Fashion",
                "base_price": Decimal("22000.00"),
                "comparison_price": Decimal("28000.00"),
                "sku": "SF-SHOE-003",
                "stock_quantity": 20,
                "is_active": True,
                "is_featured": True,
                "badge_text": "Popular",
                "description": "Clean, crisp, all-white minimalist low-top sneakers designed with breathable cushioned insoles and durable anti-slip rubber outsoles for unmatched everyday style and walking comfort.",
                "specifications": {
                    "Upper": "Synthetic Leather",
                    "Sole": "Vulcanized Rubber",
                    "Insole": "Memory Foam Cushioned",
                    "Style": "Low-Top Lace-Up"
                }
            }
        )
        p3.store = store_sunshine
        p3.base_price = Decimal("22000.00")
        p3.save()

        ProductImage.objects.get_or_create(
            product=p3,
            image="products/white-sneakers.png",
            defaults={"is_primary": True, "display_order": 1, "alt_text": "White Sneakers"}
        )

        v3, _ = ProductVariant.objects.get_or_create(
            product=p3,
            sku="SF-SHOE-WHT-42",
            defaults={"name": "42 / White", "stock_quantity": 18, "is_active": True}
        )
        v3.attribute_values.set([val_size42, val_white])

        # Product 4: Men's Casual Linen Shirt
        p4, _ = Product.objects.get_or_create(
            slug="casual-linen-shirt",
            defaults={
                "name": "Casual Linen Shirt",
                "store": store_sunshine,
                "category": cat_men,
                "brand": brand_sunshine,
                "seller_name": "Sunshine Fashion",
                "base_price": Decimal("16000.00"),
                "comparison_price": Decimal("20000.00"),
                "sku": "SF-SHT-004",
                "stock_quantity": 25,
                "is_active": True,
                "is_featured": True,
                "description": "Breathable 100% pure linen button-up shirt in light sky blue. Relaxed summer fit.",
            }
        )
        ProductImage.objects.get_or_create(
            product=p4,
            image="categories/cat-men.png",
            defaults={"is_primary": True, "display_order": 1}
        )

        # Product 5: Aviator Sunglasses
        p5, _ = Product.objects.get_or_create(
            slug="retro-aviator-sunglasses",
            defaults={
                "name": "Retro Aviator Sunglasses",
                "store": store_sunshine,
                "category": cat_accessories,
                "brand": brand_sunshine,
                "seller_name": "Sunshine Fashion",
                "base_price": Decimal("9500.00"),
                "comparison_price": Decimal("12000.00"),
                "sku": "SF-ACC-005",
                "stock_quantity": 40,
                "is_active": True,
                "is_featured": True,
                "description": "Polarized UV400 classic aviator shades with lightweight gold-tone frame.",
            }
        )
        ProductImage.objects.get_or_create(
            product=p5,
            image="categories/cat-accessories.png",
            defaults={"is_primary": True, "display_order": 1}
        )

        # Product 6: Glow Radiance Serum
        p6, _ = Product.objects.get_or_create(
            slug="glow-radiance-serum",
            defaults={
                "name": "Glow Radiance Vitamin C Serum",
                "store": store_sunshine,
                "category": cat_beauty,
                "brand": brand_sunshine,
                "seller_name": "Sunshine Fashion",
                "base_price": Decimal("12500.00"),
                "comparison_price": Decimal("15000.00"),
                "sku": "SF-BTY-006",
                "stock_quantity": 35,
                "is_active": True,
                "is_featured": True,
                "description": "Deep hydrating and brightening botanical facial serum with hyaluronic acid and niacinamide.",
            }
        )
        ProductImage.objects.get_or_create(
            product=p6,
            image="categories/cat-beauty.png",
            defaults={"is_primary": True, "display_order": 1}
        )

        # 8. Reviews for Elegant Midi Dress (Screen 4: 24 reviews, 5-star)
        Review.objects.get_or_create(
            product=p1,
            customer_name="Ngozi Eze",
            defaults={
                "rating": 5,
                "title": "Absolutely stunning dress!",
                "comment": "The fabric quality exceeded my expectations. Hugs the curves beautifully and received so many compliments at my friend's wedding in Lagos!",
                "is_verified_purchase": True,
                "is_moderated": True
            }
        )
        Review.objects.get_or_create(
            product=p1,
            customer_name="Halima Abubakar",
            defaults={
                "rating": 5,
                "title": "Fast delivery & true to size",
                "comment": "Delivered in Abuja within 24 hours. The burgundy color is rich and elegant. Will definitely order in black too.",
                "is_verified_purchase": True,
                "is_moderated": True
            }
        )

        # 9. Recent Orders for Merchant Dashboard (Screen 2 orders table)
        # #OHU1250: ₦28,000 (Paid • Oct 27, 2026) -> Completed
        # #OHU1249: ₦15,500 (Paid • Oct 27, 2026) -> Completed
        # #OHU1248: ₦42,000 (Pending • Oct 27, 2026) -> Pending
        # #OHU1247: ₦12,800 (Paid • Oct 26, 2026) -> Completed
        orders_data = [
            {
                "ref": "OHU1250",
                "total": Decimal("28000.00"),
                "subtotal": Decimal("28000.00"),
                "shipping": Decimal("0.00"),
                "payment_status": Order.PaymentStatus.PAID,
                "order_status": Order.OrderStatus.COMPLETED,
                "fulfillment_status": Order.FulfillmentStatus.DELIVERED,
                "product": p1,
                "variant": v1_m,
                "quantity": 1,
                "date_offset_hours": 12,
            },
            {
                "ref": "OHU1249",
                "total": Decimal("15500.00"),
                "subtotal": Decimal("15500.00"),
                "shipping": Decimal("0.00"),
                "payment_status": Order.PaymentStatus.PAID,
                "order_status": Order.OrderStatus.COMPLETED,
                "fulfillment_status": Order.FulfillmentStatus.DELIVERED,
                "product": p2,
                "variant": v2,
                "quantity": 1,
                "date_offset_hours": 18,
            },
            {
                "ref": "OHU1248",
                "total": Decimal("42000.00"),
                "subtotal": Decimal("40000.00"),
                "shipping": Decimal("2000.00"),
                "payment_status": Order.PaymentStatus.PENDING,
                "order_status": Order.OrderStatus.CONFIRMED,
                "fulfillment_status": Order.FulfillmentStatus.PROCESSING,
                "product": p3,
                "variant": v3,
                "quantity": 2,
                "date_offset_hours": 24,
            },
            {
                "ref": "OHU1247",
                "total": Decimal("12800.00"),
                "subtotal": Decimal("12800.00"),
                "shipping": Decimal("0.00"),
                "payment_status": Order.PaymentStatus.PAID,
                "order_status": Order.OrderStatus.COMPLETED,
                "fulfillment_status": Order.FulfillmentStatus.DELIVERED,
                "product": p5,
                "variant": None,
                "quantity": 1,
                "date_offset_hours": 40,
            },
        ]

        for od in orders_data:
            ord_obj, created = Order.objects.get_or_create(
                order_reference=od["ref"],
                defaults={
                    "store": store_sunshine,
                    "customer": merchant_user,
                    "customer_name": "Chinedu Okafor",
                    "customer_email": "chinedu@example.com",
                    "customer_phone": "+234 801 234 5678",
                    "shipping_recipient_name": "Chinedu Okafor",
                    "shipping_phone": "+234 801 234 5678",
                    "shipping_street_address": "128, Ganiyu Street, GRA",
                    "shipping_city": "Abuja",
                    "shipping_state": "FCT",
                    "shipping_country": "Nigeria",
                    "items_subtotal": od["subtotal"],
                    "shipping_fee": od["shipping"],
                    "total_amount": od["total"],
                    "payment_status": od["payment_status"],
                    "order_status": od["order_status"],
                    "fulfillment_status": od["fulfillment_status"],
                    "payment_method": "card",
                }
            )
            if created or not ord_obj.items.exists():
                OrderItem.objects.create(
                    order=ord_obj,
                    product=od["product"],
                    variant=od["variant"],
                    product_name=od["product"].name,
                    variant_name=od["variant"].name if od["variant"] else "",
                    sku=od["variant"].sku if od["variant"] else od["product"].sku,
                    unit_price=od["subtotal"],
                    quantity=od["quantity"],
                    line_total=od["subtotal"],
                )

        # 10. Campaigns & Coupons
        Campaign.objects.get_or_create(
            slug="kego-mega-flash-2026",
            defaults={
                "title": "Style That Speaks You",
                "badge_title": "Mega Flash",
                "subtitle": "Discover trendy, classy and affordable collections",
                "discount_label": "Up to 50% OFF",
                "bg_color": "#FFC928",
                "text_color": "#111111",
                "button_text": "Shop Now",
                "is_active": True,
                "start_date": timezone.now(),
            }
        )

        Coupon.objects.get_or_create(
            code="OHUAMI20",
            defaults={
                "description": "20% Discount across all partner stores",
                "discount_type": Coupon.DiscountType.PERCENTAGE,
                "discount_value": Decimal("20.00"),
                "min_order_value": Decimal("10000.00"),
                "max_discount_amount": Decimal("10000.00"),
                "usage_limit": 500,
                "is_active": True,
            }
        )

        self.stdout.write(self.style.SUCCESS("OHUAMI multi-tenant catalog and Sunshine Fashion store successfully seeded!"))
