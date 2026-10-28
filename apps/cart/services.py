from django.db import transaction
from .models import Cart, CartItem
from apps.catalog.models import Product, ProductVariant
from apps.promotions.models import Coupon


class CartService:
    @staticmethod
    def get_or_create_cart(request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            # If session cart exists, merge into user cart
            session_key = request.session.session_key
            if session_key:
                session_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
                if session_cart:
                    CartService.merge_carts(session_cart, cart)
            return cart
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)
            return cart

    @staticmethod
    def merge_carts(source_cart, target_cart):
        with transaction.atomic():
            for item in source_cart.items.all():
                existing = target_cart.items.filter(product=item.product, variant=item.variant).first()
                if existing:
                    existing.quantity += item.quantity
                    existing.save()
                else:
                    item.cart = target_cart
                    item.save()
            if source_cart.coupon and not target_cart.coupon:
                target_cart.coupon = source_cart.coupon
                target_cart.save()
            source_cart.delete()

    @staticmethod
    def add_item(cart, product_id, variant_id=None, quantity=1):
        product = Product.objects.get(id=product_id, is_active=True)
        variant = None
        if variant_id:
            variant = ProductVariant.objects.get(id=variant_id, product=product, is_active=True)

        # Inventory check
        available = variant.stock_quantity if variant else product.available_stock
        if available <= 0:
            return False, "This product is currently out of stock."

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': min(quantity, available)}
        )
        if not created:
            new_qty = item.quantity + quantity
            if new_qty > available:
                new_qty = available
            item.quantity = new_qty
            item.save()
        return True, "Added to cart successfully."

    @staticmethod
    def update_item_qty(cart, item_id, quantity):
        try:
            item = cart.items.get(id=item_id)
            if quantity <= 0:
                item.delete()
                return True, "Item removed."
            available = item.variant.stock_quantity if item.variant else item.product.available_stock
            if quantity > available:
                return False, f"Only {available} units available."
            item.quantity = quantity
            item.save()
            return True, "Quantity updated."
        except CartItem.DoesNotExist:
            return False, "Item not found in cart."

    @staticmethod
    def remove_item(cart, item_id):
        cart.items.filter(id=item_id).delete()
        return True, "Item removed."

    @staticmethod
    def apply_coupon(cart, code):
        code = code.upper().strip()
        try:
            coupon = Coupon.objects.get(code=code)
            is_valid, msg = coupon.is_valid(cart.subtotal, cart.user)
            if not is_valid:
                return False, msg
            cart.coupon = coupon
            cart.save()
            return True, f"Coupon '{code}' applied successfully!"
        except Coupon.DoesNotExist:
            return False, "Invalid coupon code."

    @staticmethod
    def remove_coupon(cart):
        cart.coupon = None
        cart.save()
        return True, "Coupon removed."
