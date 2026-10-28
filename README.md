# OHUAMI — Multi-Tenant African Commerce Platform

> **Brand:** OHUAMI  
> **Parent Company:** Cube Tech Enterprises  
> **Tagline:** *Your market. Your business. Your growth.*  
> **Secondary Positioning:** *Commerce made for your ambition.*  
> **Brand Palette:** Brand Red (`#E53935`), Deep Black (`#111111`), Accent Yellow (`#FFC928`), Pure White (`#FFFFFF`).  
> **Typography:** Montserrat (`'Montserrat', system-ui, sans-serif`)  
> **Primary Specification:** Pixel-accurate realization of the approved OHUAMI Brand Identity Showcase and Commerce SaaS UI Showcase.

---

## 1. Architectural Highlights

OHUAMI is a production-grade, multi-tenant digital commerce SaaS engine built on Python/Django:

1. **Multi-Tenancy & Merchant Scoping:**
   - Dedicated `Store` entity with independent branding, tagline, description, plan tiers, and follower count.
   - Products, inventory, orders, and customer accounts are strictly tenant-isolated to prevent cross-tenant data leakage.
   - Dynamic store routing (`/catalog/store/<store_slug>/` e.g. `/catalog/store/sunshine-fashion/`).
2. **6 Reference-Matched Core Experience Surfaces:**
   - **Screen 1: Marketing Homepage (`/`):** Dark hero (`#111111`), "Your market. **Your business.** Your growth.", "Start for Free" (Yellow CTA), "Watch Demo", floating sales metrics card (₦1,245,600), live store card, and 5-pillar bottom feature strip (Online Stores, Inventory, Orders & Payments, Analytics, Automation & AI).
   - **Screen 2: Merchant Dashboard (`/dashboard/`):** Left dark sidebar with OHUAMI branding, active yellow pill navigation, greeting ("Good morning, Chinedu! 👋"), 4 KPI cards (₦842,750 sales, 36 orders, 1,248 customers, 52 products), sales overview line chart with yellow area fill, recent orders table with status badges.
   - **Screen 3: Customer Storefront (`/catalog/store/sunshine-fashion/`):** "Sunshine Fashion" store header with "Follow" button, banner ("Style that speaks you. Trendy. Classy. Affordable."), 6 circular category pills (Women, Men, Bags, Shoes, Accessories, Beauty), and featured product grid.
   - **Screen 4: Product Detail Page (`/catalog/product/elegant-midi-dress/`):** Left vertical gallery with 4 thumbnails and large main image with "-20%" badge, right side with title ("Elegant Midi Dress"), 5-star rating (24 reviews), price ₦28,000 / ₦35,000, description, color swatches (Burgundy, Black, Cream), size pills (S, M, L, XL), quantity selector, "Add to Cart", and yellow "Buy Now" CTA.
   - **Screen 5: Shopping Cart (`/cart/`):** Line items with variant tags, quantity counter, delete action, order summary (Subtotal ₦68,500, Shipping ₦2,000, Total ₦70,500), and yellow "Proceed to Checkout" button.
   - **Screen 6: Checkout (`/checkout/`):** 1. Shipping Information (Chinedu Okafor, 128 Ganiyu St, Abuja, FCT), 2. Payment Method (Card, Bank Transfer, USSD, Pay on Delivery), Order Summary, and yellow "Pay Now" button.
3. **Official Vector Logo Suite (`static/images/`):**
   - Awning-inspired digital market symbol with 4 red scallops, yellow crescent curve, and 4 connected nodes.
   - `ohuami-icon.svg`: Standalone digital market symbol.
   - `ohuami-wordmark.svg`: Montserrat bold wordmark with yellow accent triangle inside 'A'.
   - `ohuami-horizontal.svg`: Light-mode horizontal lockup.
   - `ohuami-horizontal-dark.svg`: Dark-mode horizontal lockup.
   - `ohuami-stacked.svg`: Stacked logo for vertical placements.
   - `ohuami-app-icon-dark.svg` & `ohuami-app-icon-light.svg`: App launcher icons.
   - `ohuami-favicon.svg`: Browser tab icon.
4. **Nigerian Payment Gateway Architecture:**
   - Native **Paystack** integration (Cards, Bank Transfer, USSD) with secure server-side transaction initialization, status verification, and HMAC-SHA512 webhook signature verification.
   - Built-in **Sandbox / Development Adapter** allowing full end-to-end purchasing and verification without external network dependency.

---

## 2. Brand Design Tokens

All colors, radii, and typography tokens are centralized in `static/css/theme.css`:

| Token | Hex Value | Role |
|-------|-----------|------|
| **Brand Red** | `#E53935` | Awning scallops, sale badges, discount highlights, urgent alerts |
| **Brand Black** | `#111111` | Headings, dark marketing hero background, sidebar, high contrast |
| **Brand Yellow** | `#FFC928` | Primary conversion CTAs ("Start for Free", "Buy Now", "Proceed to Checkout", "Pay Now"), active sidebar pill, rating stars |
| **Pure White** | `#FFFFFF` | Storefront surfaces, cards, input panels |
| **Verified Green** | `#10B981` | Success states, live store badges, delivered order badges |

---

## 3. Demo Credentials & Test Accounts

| Account Role | Email | Password | Access / Scope |
|--------------|-------|----------|----------------|
| **Super Administrator** | `admin@ohuami.com` | `Admin@123456` | Full Django Admin (`/admin/`) |
| **Sunshine Fashion Merchant** | `chinedu@example.com` | `Password@123` | Merchant Dashboard (`/dashboard/`) |
| **Customer Account** | `customer@example.com` | `Customer@123` | Storefront & Checkout (`/cart/`, `/checkout/`) |

---

## 4. Quick Start & Setup

### 1. Activate Virtual Environment
```bash
# Windows
.\.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Apply Database Migrations
```bash
python manage.py migrate
```

### 4. Seed OHUAMI Multi-Tenant Demo Data
```bash
python manage.py seed_data
```

### 5. Start Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```

### 6. Run Automated Test Suite
```bash
pytest
```
*Current test suite: 25 tests passing (100% pass rate).*

---

## 5. Visual Deliverables & Verification Screenshots

Screenshots captured directly via automated browser testing:
- **Screen 1 (Marketing Homepage):** `ohuami_screen_1_marketing_home.png`
- **Screen 2 (Merchant Dashboard):** `ohuami_screen_2_merchant_dashboard.png`
- **Screen 3 (Customer Storefront):** `ohuami_screen_3_storefront.png`
- **Screen 4 (Product Detail Page):** `ohuami_screen_4_product_detail.png`
- **Screen 5 (Shopping Cart):** `ohuami_screen_5_cart.png`
- **Screen 6 (Checkout):** `ohuami_screen_6_checkout.png`
- **Mobile Responsive Views:** `ohuami_screen_1_marketing_home_mobile.png`, `ohuami_screen_3_storefront_mobile.png`, `ohuami_screen_4_product_detail_mobile.png`, `ohuami_screen_5_cart_mobile.png`, `ohuami_screen_6_checkout_mobile.png`.
