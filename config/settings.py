import os
from pathlib import Path
import environ

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, 'django-insecure-cubetech-enterprise-commerce-super-secret-key-2026'),
    ALLOWED_HOSTS=(list, ['*']),
    PAYSTACK_PUBLIC_KEY=(str, 'pk_test_sample_cubetech_public'),
    PAYSTACK_SECRET_KEY=(str, 'sk_test_sample_cubetech_secret'),
    PAYSTACK_WEBHOOK_SECRET=(str, 'whsec_sample_cubetech'),
    FLUTTERWAVE_PUBLIC_KEY=(str, 'FLWPUBK_TEST-sample'),
    FLUTTERWAVE_SECRET_KEY=(str, 'FLWSECK_TEST-sample'),
    FLUTTERWAVE_WEBHOOK_SECRET=(str, 'flw_whsec_sample'),
)

# Load .env file if it exists
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(env_file)

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third-party
    'corsheaders',
    'rest_framework',
    
    # Internal Modular Apps
    'apps.core.apps.CoreConfig',
    'apps.accounts.apps.AccountsConfig',
    'apps.catalog.apps.CatalogConfig',
    'apps.inventory.apps.InventoryConfig',
    'apps.promotions.apps.PromotionsConfig',
    'apps.cart.apps.CartConfig',
    'apps.checkout.apps.CheckoutConfig',
    'apps.orders.apps.OrdersConfig',
    'apps.payments.apps.PaymentsConfig',
    'apps.reviews.apps.ReviewsConfig',
    'apps.wishlist.apps.WishlistConfig',
    'apps.support.apps.SupportConfig',
    'apps.dashboard.apps.DashboardConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Default to SQLite for local development and tests, configurable to PostgreSQL via DATABASE_URL
DATABASES = {
    'default': env.db('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400 * 30  # 30 days
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF Configuration
CSRF_COOKIE_HTTPONLY = False  # Required for HTMX/JavaScript fetch to read csrf token
CSRF_COOKIE_SAMESITE = 'Lax'

# Authentication URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'

# Brand & Payment Settings
BRAND_NAME = "OHUAMI"
BRAND_TAGLINE = "Your market. Your business. Your growth."
BRAND_SECONDARY = "Commerce made for your ambition."
PARENT_COMPANY = "Cube Tech Enterprises"
BRAND_COLORS = {
    'RED': '#E53935',
    'BLACK': '#111111',
    'YELLOW': '#FFC928',
    'WHITE': '#FFFFFF',
}

DEFAULT_CURRENCY = 'NGN'
DEFAULT_CURRENCY_SYMBOL = '₦'

# Payment Gateways
PAYSTACK_PUBLIC_KEY = env('PAYSTACK_PUBLIC_KEY')
PAYSTACK_SECRET_KEY = env('PAYSTACK_SECRET_KEY')
PAYSTACK_WEBHOOK_SECRET = env('PAYSTACK_WEBHOOK_SECRET')

FLUTTERWAVE_PUBLIC_KEY = env('FLUTTERWAVE_PUBLIC_KEY')
FLUTTERWAVE_SECRET_KEY = env('FLUTTERWAVE_SECRET_KEY')
FLUTTERWAVE_WEBHOOK_SECRET = env('FLUTTERWAVE_WEBHOOK_SECRET')

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Cross-Origin Resource Sharing (CORS) Settings
from corsheaders.defaults import default_headers, default_methods

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-store-key',
    'x-store-id',
    'x-merchant-id',
]
CORS_ALLOW_METHODS = list(default_methods) + [
    'PATCH',
    'DELETE',
]
