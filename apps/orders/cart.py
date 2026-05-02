from .models import Cart, CartItem


class SessionCart:

    def __init__(self, request):
        if not request.session.session_key:
            request.session.create()

        self.session_key = request.session.session_key
        self.user        = request.user if request.user.is_authenticated else None

        if self.user:
            # logged-in: get or create a cart for this user
            self.cart, created = Cart.objects.get_or_create(
                user=self.user,
                defaults={
                    'session_key': self.session_key,
                    'is_abandoned': False,
                }
            )
            # merge any guest session cart into the user cart on first login
            if created:
                self._merge_session_cart()
            else:
                # update session key to current in case they logged in on a new device
                if self.cart.session_key != self.session_key:
                    self._merge_session_cart()
        else:
            # guest: use session key
            self.cart, _ = Cart.objects.get_or_create(
                session_key=self.session_key,
                user=None,
                defaults={'is_abandoned': False}
            )

    def _merge_session_cart(self):
        """
        When a user logs in, merge their guest session cart
        into their user cart, then delete the guest cart.
        """
        try:
            guest_cart = Cart.objects.get(
                session_key=self.session_key,
                user=None,
            )
        except Cart.DoesNotExist:
            return

        for guest_item in guest_cart.items.select_related('product', 'variant').all():
            existing = CartItem.objects.filter(
                cart=self.cart,
                product=guest_item.product,
                variant=guest_item.variant,
            ).first()

            if existing:
                existing.quantity += guest_item.quantity
                existing.save()
            else:
                guest_item.cart = self.cart
                guest_item.save()

        guest_cart.delete()

    # ─── READ ───

    def get_items(self):
        return self.cart.items.select_related(
            'product', 'variant', 'product__collection'
        ).filter(product__is_active=True)

    def get_total(self):
        return sum(
            (item.variant.final_price if item.variant else item.product.price) * item.quantity
            for item in self.get_items()
        )

    def get_count(self):
        return sum(item.quantity for item in self.get_items())

    # ─── WRITE ───

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