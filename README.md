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
3. **Official Master Logo & Icon Suite (`static/images/`):**
   - Redesigned 3-panel digital market awning symbol with angled chamfers, yellow crescent smile curve, and 3 connected commerce nodes (2 circular dots + 1 rounded geometric cube).
   - Wordmark featuring bold geometric typography with official brand yellow accent triangle nested inside the letter 'A'.
   - Official tagline: *"Your market, Your Business, Your growth."*
   - `ohuami-icon.png` & `ohuami-icon.svg`: Standalone transparent digital market symbol.
   - `ohuami-horizontal.png` & `ohuami-horizontal.svg`: Master horizontal lockup for light backgrounds (transparent and solid white variants).
   - `ohuami-horizontal-dark.png` & `ohuami-horizontal-dark.svg`: Master horizontal lockup for dark surfaces (transparent and `#0c0c0b` solid variants).
   - `ohuami-stacked.png` & `ohuami-stacked.svg`: Stacked vertical lockup on transparent background.
   - `ohuami-stacked-dark.png` & `ohuami-stacked-dark.svg`: Stacked vertical lockup on dark background.
   - `ohuami-app-icon-dark.png` & `ohuami-app-icon-dark.svg`: Dark squircle app launcher icon with full-color awning and white nodes.
   - `ohuami-app-icon-red.png` & `ohuami-app-icon-red.svg`: Brand red squircle app launcher icon with pure white symbol.
   - `ohuami-favicon.png`, `ohuami-favicon.svg` & `favicon.ico`: High-resolution browser favicon suite.
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
| **Super Administrator** | `admin@ohuami.com` | `Admin@123456` | Full Control Panel (`/admin/control-panel/` & `/admin/`) |
| **Sunshine Fashion Merchant** | `chinedu@example.com` | `Password@123` | Merchant Dashboard (`/dashboard/`) |
| **Customer Account** | `customer@example.com` | `Customer@123` | Storefront, Profile & Checkout (`/cart/`, `/checkout/`, `/accounts/profile/`) |

---

## 4. Super Admin Control Center & Multi-Merchant Governance

The platform features an executive **Super Admin Control Center** accessible at `/admin/control-panel/` (and `/platform-admin/`), as well as a branded Django ModelAdmin interface at `/admin/`:

1. **Merchants & Stores Governance:**
   - Multi-tenant directory with live storefront links, product/order tallies, and store owner records.
   - Status transitions (`Active`, `Pending Review`, `Suspended`, `Archived`).
   - KYC Verification with BVN (Bank Verification Number) check and audit verification notes.
   - Per-merchant commission overrides (`commission_rate_override`), custom domains (`custom_domain`), and storage quotas.
   - Direct batch actions in Django Admin: Approve Stores, Suspend Stores, Verify BVN.

2. **Global Stores Settings:**
   - Singleton configuration (`StoreSetting`) controlling platform brand identity (`OHUAMI`), parent company (`Cube Tech Enterprises`), and taglines.
   - Platform default commission percentage (default `5.0%`) and fixed transaction processing fees (₦100.00).
   - Global delivery defaults: standard shipping rate (₦2,000.00), free shipping threshold (₦50,000.00), and supported currencies (`NGN, USD, GBP, EUR`).
   - Operational switches: Real-time Maintenance Mode with custom alert message, Merchant Registration toggle, and Mandatory KYC enforcement.

3. **Multi-Merchant Tiers & Plans:**
   - 4 Pre-configured subscription tiers:
     - **Free Tier:** ₦0/mo, 7.0% commission, 25 products limit, 1 staff seat, 500 MB storage.
     - **Starter Plan:** ₦15,000/mo, 5.0% commission, 250 products limit, 3 staff seats, 2 GB storage.
     - **Pro Plan:** ₦35,000/mo, 3.5% commission, 2,500 products limit, 10 staff seats, 10 GB storage, custom domain support.
     - **Enterprise Custom:** ₦85,000/mo, 2.0% commission, unlimited products, 50 staff seats, 100 GB storage, dedicated support.
   - In-place AJAX updates for subscription prices, fee structures, and product limits.

4. **Modular Platform Services & Feature Flags:**
   - 9 Modular switchboard service toggles:
     - `ai_automation`: AI Product Descriptions & Intelligent Pricing.
     - `whatsapp_commerce`: WhatsApp Business Storefront & Automated Notifications.
     - `custom_domains`: White-label Custom Domains & SSL Management.
     - `pos_terminal`: In-Store Point of Sale & Physical Hardware Sync.
     - `multi_currency`: Multi-Currency Checkout (NGN, USD, GBP, EUR).
     - `escrow_protection`: Buyer Protection Escrow & Dispute Resolution.
     - `automated_logistics`: Automated Carrier Dispatch & Tracking.
     - `advanced_analytics`: Real-time Funnel & Predictive Cohort Analytics.
     - `abandoned_cart_recovery`: Automated WhatsApp & Email Cart Recovery.
   - Instant AJAX toggle with automatic state persistence and `AuditLog` generation.

5. **Security, CSRF & Audit Trail:**
   - Strict `is_superuser` and `User.Role.ADMIN` gating with automatic redirect for unauthorized users.
   - Complete audit trail tracking user, IP address, target entity, timestamp, and modification details in `AuditLog`.

---

## 5. Ancillary Pages, Forms & Full-Stack Wiring

Beyond the 6 core visual showcase screens, all remaining customer and merchant interfaces are fully functional and wired to persistent database models:

1. **Product Reviews & Ratings (`/reviews/submit/<id>/`):**
   - Dynamic 5-star rating selector, headline, and detailed review input with verified buyer badging and star rating distribution breakdown.
2. **Support & Ticketing Portal (`/support/contact/`):**
   - 2-Column support interface with auto-generated ticket references (`SUP-XXXXXXXX`), customer pre-population, official Cube Tech contact details, and an interactive FAQ accordion.
3. **Customer Account Hub & Address Book (`/accounts/profile/`):**
   - Personal profile editor (`ProfileUpdateForm`), complete address book CRUD (add, delete, set default), past order history with tracking links, and security password reset.
4. **Order Tracking & Itemized Receipt (`/orders/<order_ref>/`):**
   - 4-Stage visual fulfillment progress bar (`Placed` → `Payment Verified` → `Processing` → `Dispatched / Delivered`), full itemized receipt breakdown with images, delivery address, and print action.
5. **Interactive Shopping Cart Promo Codes (`/cart/` & `/promotions/coupons/`):**
   - Asynchronous coupon application and removal directly inside the cart with instant discount calculations and 1-click "Apply to Cart" from the promotions center.
6. **Merchant Operations & Complete CRUD/CORS System:**
   - **Catalog CRUD (`/dashboard/products/`):** Full creation, editing, active status toggle, deletion, and search with tier quota meter.
   - **Orders Management (`/dashboard/orders/`):** View details, update statuses, cancel with inventory restock, and manual in-store/phone order creator (`/dashboard/orders/new/`).
   - **Logistics & Dispatch Control (`/dashboard/logistics/`):** Carrier/rider registration, vehicle fleet management, automatic tracking number generation (`OHU-TRK-...`), and milestone status progression.
   - **Customer Directory & CRM (`/dashboard/customers/`):** Segment customers with tags (`VIP`, `Regular`, `New`, `Wholesale`), analyze lifetime spend (LTV), order history, and private merchant notes.
   - **Agents & Staff (`/dashboard/agents/`):** Invite staff members, assign roles (`Store Manager`, `Support Agent`, `Inventory`, `Dispatch`), and toggle granular permissions within tier quota seats.
   - **CORS & Headless REST API (`/dashboard/api-cors/` & `/dashboard/api/...`):** Per-store CORS allowed origins configuration, secret API key generation, and full RESTful API endpoints for headless storefronts and mobile apps.
7. **Product Photos & Real-Time Storefront Live Preview (`/dashboard/products/new/` & `.../edit/`):**
   - **Cover Photo & Batch Gallery Upload:** Dedicated dropzone for primary cover photo plus multi-file uploader (`MultipleFileField` / `MultipleFileInput`) for secondary angles and lifestyle shots.
   - **Gallery Photo Management:** Existing photos gallery grid showing "Cover Photo" badge, one-click "Set Primary" promotion, and individual photo deletion.
   - **Real-Time Split-Screen PDP Preview:** 12-column layout (7-col editing form + 5-col sticky preview) faithfully mirroring Screen 4 (Product Detail Page) in real time:
     - Dynamic title, category breadcrumb, rating stars (24 reviews), price + comparison price, auto-calculated discount percentage badge (`-20%`), live description, color swatches, size pills, `Add to Cart`, and yellow `Buy Now` CTA.
     - Interactive Device Switcher (`[ 💻 Desktop ]` and `[ 📱 Mobile ]`).
     - Zero latency client-side image preview using `FileReader.readAsDataURL` updating both thumbnails and PDP hero images immediately upon file selection.
8. **Global Brand Footer (`templates/base.html`):**
   - 4-Column footer with OHUAMI brand lockup, catalog links, customer care, merchant portal links, legal info, and newsletter subscription form.

---

## 6. Quick Start & Setup

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
*Current test suite: **44 tests passing (100% pass rate)*** across customer cart, catalog, checkout, promotions, merchant dashboard, paystack webhooks, security isolation, super admin control endpoints, reviews, support, customer profile/address book, order tracking, product image upload/gallery management, and complete merchant CRUD/CORS operations (products, orders, agents, dispatch, logistics, customers, headless REST API).

---

## 7. Visual Deliverables & Verification Screenshots

Screenshots captured directly via automated browser testing:
- **Updated Marketing Homepage (with New Master Logo):** `ohuami_updated_home_logo.png`
- **Updated Storefront Header (with New Master Logo):** `ohuami_updated_storefront_logo.png`
- **Updated Merchant Dashboard (with New Master Logo):** `ohuami_updated_merchant_dashboard_logo.png`
- **Updated Django Admin Control Panel (with New Master Logo):** `ohuami_updated_django_admin_logo.png`
- **Product Create & Split-Screen Live Preview:** `ohuami_product_create_live_preview.png`
- **Product Create Preview (Mobile View Switcher):** `ohuami_product_create_mobile_preview.png`
- **Product Edit & Existing Photo Gallery:** `ohuami_product_edit_live_preview.png`
- **Super Admin Control Center:** `ohuami_super_admin_control_panel.png`
- **Super Admin Control Center (Mobile):** `ohuami_super_admin_control_panel_mobile.png`
- **Customized Django Admin Index:** `ohuami_django_admin_index.png`
- **Multi-Tenant Stores Directory Admin:** `ohuami_admin_stores_list.png`
- **Screen 1 (Marketing Homepage):** `ohuami_screen_1_marketing_home.png`
- **Screen 2 (Merchant Dashboard):** `ohuami_screen_2_merchant_dashboard.png`
- **Screen 3 (Customer Storefront):** `ohuami_screen_3_storefront.png`
- **Screen 4 (Product Detail Page):** `ohuami_screen_4_product_detail.png`
- **Screen 5 (Shopping Cart):** `ohuami_screen_5_cart.png`
- **Screen 6 (Checkout):** `ohuami_screen_6_checkout.png`
- **Merchant Orders Management:** `ohuami_merchant_orders.png`
- **Merchant Products & Quota:** `ohuami_merchant_products.png`
- **Merchant Logistics & Dispatch Control:** `ohuami_merchant_logistics.png`
- **Merchant Customers & CRM:** `ohuami_merchant_customers.png`
- **Merchant Agents & Staff Directory:** `ohuami_merchant_agents.png`
- **Merchant CORS & Headless API:** `ohuami_merchant_api_cors.png`
- **Support & Ticketing Portal:** `ohuami_support_contact.png`
- **Product Reviews & Rating Breakdown:** `ohuami_product_reviews.png`
- **Mobile Responsive Views:** `ohuami_screen_1_marketing_home_mobile.png`, `ohuami_screen_3_storefront_mobile.png`, `ohuami_screen_4_product_detail_mobile.png`, `ohuami_screen_5_cart_mobile.png`, `ohuami_screen_6_checkout_mobile.png`.
