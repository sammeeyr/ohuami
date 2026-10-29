from django.apps import AppConfig


class DashboardConfig(AppConfig):
    name = 'apps.dashboard'

    def ready(self):
        try:
            from corsheaders.signals import check_request_enabled
            from apps.catalog.models import Store

            def cors_allow_merchant_store_origins(sender, request, **kwargs):
                origin = request.headers.get('Origin') or request.META.get('HTTP_ORIGIN')
                if not origin:
                    return False
                # Check all active stores for custom allowed origins
                for store in Store.objects.filter(is_active=True).only('cors_allowed_origins'):
                    if origin in store.get_cors_origins_list():
                        return True
                return False

            check_request_enabled.connect(cors_allow_merchant_store_origins)
        except Exception:
            pass
