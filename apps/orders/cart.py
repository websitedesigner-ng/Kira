from .models import Cart, CartItem


class SessionCart:

    def __init__(self, request):
        if not request.session.session_key:
            request.session.create()
        self.session_key = request.session.session_key
        self.cart, _ = Cart.objects.get_or_create(
            session_key=self.session_key,
            defaults={'is_abandoned': False}
        )

    def get_items(self):
        return self.cart.items.select_related(
            'product', 'variant'
        ).filter(product__is_active=True)

    def get_total(self):
        return sum(
            item.variant.final_price * item.quantity
            if item.variant
            else item.product.price * item.quantity
            for item in self.get_items()
        )

    def get_count(self):
        return sum(item.quantity for item in self.get_items())

    def add(self, product, variant=None, quantity=1):
        item, created = CartItem.objects.get_or_create(
            cart=self.cart,
            product=product,
            variant=variant,
            defaults={'quantity': 0}
        )
        item.quantity += quantity
        item.save()
        self.cart.is_abandoned = False
        self.cart.save(update_fields=['updated_at', 'is_abandoned'])
        return item

    def update(self, item_id, quantity):
        try:
            item = CartItem.objects.get(id=item_id, cart=self.cart)
            if quantity > 0:
                item.quantity = quantity
                item.save()
            else:
                item.delete()
        except CartItem.DoesNotExist:
            pass

    def remove(self, item_id):
        CartItem.objects.filter(id=item_id, cart=self.cart).delete()

    def clear(self):
        self.cart.items.all().delete()