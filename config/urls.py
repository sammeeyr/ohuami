from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.dashboard import super_admin_views

urlpatterns = [
    path('admin/control-panel/', super_admin_views.super_admin_control_panel, name='admin_control_panel'),
    path('platform-admin/', super_admin_views.super_admin_control_panel, name='platform_admin'),
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls', namespace='core')),
    path('catalog/', include('apps.catalog.urls', namespace='catalog')),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('checkout/', include('apps.checkout.urls', namespace='checkout')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('promotions/', include('apps.promotions.urls', namespace='promotions')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('wishlist/', include('apps.wishlist.urls', namespace='wishlist')),
    path('reviews/', include('apps.reviews.urls', namespace='reviews')),
    path('support/', include('apps.support.urls', namespace='support')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
