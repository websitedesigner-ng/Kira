from django.db import models
from apps.store.models import Product, ProductVariant

# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('confirmed',  'Confirmed'),
        ('shipped',    'Shipped'),
        ('delivered',  'Delivered'),
        ('cancelled',  'Cancelled'),
        ('refunded',   'Refunded'),
    ]

    reference     = models.CharField(max_length=32, unique=True)
    customer_name  = models.CharField(max_length=200)
    customer_email = models.EmailField()
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total          = models.DecimalField(max_digits=10, decimal_places=2)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.reference} — {self.customer_email}'


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    variant  = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price    = models.DecimalField(max_digits=10, decimal_places=2)  # price at time of purchase

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