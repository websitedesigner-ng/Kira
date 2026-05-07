import uuid
from django.db import models
from django.conf import settings
from apps.store.models import Product, ProductVariantSize   # ← updated import


class Address(models.Model):
    """
    Reusable saved address — belongs to a user account.
    """
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    label      = models.CharField(max_length=60, blank=True)
    full_name  = models.CharField(max_length=200)
    phone      = models.CharField(max_length=30)
    line1      = models.CharField(max_length=255)
    line2      = models.CharField(max_length=255, blank=True)
    city       = models.CharField(max_length=100)
    state      = models.CharField(max_length=100)
    postcode   = models.CharField(max_length=20)
    country    = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.label or "Address"} — {self.full_name}, {self.city}'

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(
                user=self.user, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def as_snapshot(self):
        return {
            'full_name': self.full_name,
            'phone':     self.phone,
            'line1':     self.line1,
            'line2':     self.line2,
            'city':      self.city,
            'state':     self.state,
            'postcode':  self.postcode,
            'country':   self.country,
        }


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped',   'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded',  'Refunded'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders'
    )
    customer_name  = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30, blank=True)

    shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders'
    )
    shipping_name     = models.CharField(max_length=200)
    shipping_phone    = models.CharField(max_length=30, blank=True)
    shipping_line1    = models.CharField(max_length=255)
    shipping_line2    = models.CharField(max_length=255, blank=True)
    shipping_city     = models.CharField(max_length=100)
    shipping_state    = models.CharField(max_length=100, blank=True)
    shipping_postcode = models.CharField(max_length=20, blank=True)
    shipping_country  = models.CharField(max_length=100)

    reference  = models.CharField(max_length=32, unique=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes      = models.TextField(blank=True)
    total      = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.reference} — {self.customer_email}'

    @property
    def shipping_address_display(self):
        parts = filter(None, [
            self.shipping_name,
            self.shipping_line1,
            self.shipping_line2,
            self.shipping_city,
            self.shipping_state,
            self.shipping_postcode,
            self.shipping_country,
        ])
        return ', '.join(parts)


class OrderItem(models.Model):
    order        = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product      = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')

    # ← Now points to ProductVariantSize (carries variant name + size + price)
    variant_size = models.ForeignKey(
        ProductVariantSize, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='order_items'
    )

    quantity = models.PositiveIntegerField(default=1)
    price    = models.DecimalField(max_digits=10, decimal_places=2)

    # Snapshot fields — frozen at time of purchase so the line item
    # is always readable even if the variant/size is later deleted.
    snapshot_variant_name = models.CharField(max_length=100, blank=True)  # e.g. "Black"
    snapshot_size         = models.CharField(max_length=20, blank=True)   # e.g. "M"
    snapshot_sku          = models.CharField(max_length=100, blank=True)

    def __str__(self):
        variant_label = ''
        if self.snapshot_variant_name:
            variant_label = f' ({self.snapshot_variant_name} / {self.snapshot_size})'
        return f'{self.quantity}x {self.product.name}{variant_label} — Order {self.order.reference}'

    @property
    def subtotal(self):
        return self.price * self.quantity

    @property
    def variant_display(self):
        """Human-readable label for templates — uses snapshot so always safe."""
        if self.snapshot_variant_name and self.snapshot_size:
            return f'{self.snapshot_variant_name} / {self.snapshot_size}'
        if self.snapshot_variant_name:
            return self.snapshot_variant_name
        if self.snapshot_size:
            return self.snapshot_size
        return '—'


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='cart'
    )
    session_key    = models.CharField(max_length=40, unique=True)
    customer_email = models.EmailField(blank=True, null=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    is_abandoned   = models.BooleanField(default=False)

    def __str__(self):
        return f'Cart {self.session_key}'


class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    # ← Now points to ProductVariantSize
    variant_size = models.ForeignKey(
        ProductVariantSize, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cart_items'
    )

    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        label = f' ({self.variant_size})' if self.variant_size else ''
        return f'{self.quantity}x {self.product.name}{label}'

    @property
    def unit_price(self):
        return self.variant_size.final_price if self.variant_size else self.product.price

    @property
    def subtotal(self):
        return self.unit_price * self.quantity