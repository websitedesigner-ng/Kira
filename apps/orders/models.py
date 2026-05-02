from django.db import models
from apps.store.models import Product, ProductVariant

from django.db import models
from django.contrib.auth.models import User
from apps.store.models import Product, ProductVariant


class Address(models.Model):
    """
    Reusable saved address — belongs to a user account.
    Created when a user saves an address during checkout or in their profile.
    """
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label      = models.CharField(max_length=60, blank=True)  # e.g. "Home", "Office"
    full_name  = models.CharField(max_length=200)
    phone      = models.CharField(max_length=30, blank=True)
    line1      = models.CharField(max_length=255)
    line2      = models.CharField(max_length=255, blank=True)
    city       = models.CharField(max_length=100)
    state      = models.CharField(max_length=100, blank=True)
    postcode   = models.CharField(max_length=20, blank=True)
    country    = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.label or "Address"} — {self.full_name}, {self.city}'

    def save(self, *args, **kwargs):
        # enforce one default per user
        if self.is_default:
            Address.objects.filter(
                user=self.user, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def as_snapshot(self):
        """Returns a dict for snapshotting onto an order."""
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

    # ─── WHO ───
    # nullable so guest orders work; filled when user is logged in
    user           = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders'
    )
    customer_name  = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30, blank=True)

    # ─── WHERE ───
    # snapshot of the address at time of order — never changes even if user
    # edits their saved address later
    shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders',
        help_text='Linked saved address, if any'
    )
    # denormalized snapshot fields — always populated
    shipping_name     = models.CharField(max_length=200)
    shipping_phone    = models.CharField(max_length=30, blank=True)
    shipping_line1    = models.CharField(max_length=255)
    shipping_line2    = models.CharField(max_length=255, blank=True)
    shipping_city     = models.CharField(max_length=100)
    shipping_state    = models.CharField(max_length=100, blank=True)
    shipping_postcode = models.CharField(max_length=20, blank=True)
    shipping_country  = models.CharField(max_length=100)

    # ─── ORDER ───
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
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    variant  = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price    = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity}x {self.product.name} (Order {self.order.reference})'

    @property
    def subtotal(self):
        return self.price * self.quantity


class Cart(models.Model):
    session_key  = models.CharField(max_length=40, unique=True)
    customer_email = models.EmailField(blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    is_abandoned = models.BooleanField(default=False)  # set via management command

    def __str__(self):
        return f'Cart {self.session_key}'


class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant  = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'


class ProductView(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    session_key = models.CharField(max_length=40)
    viewed_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['product', 'viewed_at']),
        ]

    def __str__(self):
        return f'{self.product.name} view'