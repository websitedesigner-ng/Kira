from django.contrib import admin
from django.utils.html import format_html
from .models import Address, Order, OrderItem, Cart, CartItem


# ═══════════════════════════════════════════
# ADDRESS
# ═══════════════════════════════════════════

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display  = ('full_name', 'user', 'city', 'country', 'is_default', 'created_at')
    list_filter   = ('country', 'is_default')
    search_fields = ('full_name', 'user__email', 'city', 'line1')
    readonly_fields = ('created_at',)
    raw_id_fields   = ('user',)


# ═══════════════════════════════════════════
# ORDER ITEMS (inline)
# ═══════════════════════════════════════════

class OrderItemInline(admin.TabularInline):
    model           = OrderItem
    extra           = 0
    readonly_fields = ('product', 'variant_display', 'quantity', 'price', 'subtotal',
                       'snapshot_variant_name', 'snapshot_size', 'snapshot_sku')
    fields          = ('product', 'variant_display', 'snapshot_variant_name',
                       'snapshot_size', 'quantity', 'price', 'subtotal')
    can_delete      = False

    def subtotal(self, obj):
        return f'£{obj.subtotal:,.2f}'
    subtotal.short_description = 'Subtotal'

    def variant_display(self, obj):
        return obj.variant_display
    variant_display.short_description = 'Variant / Size'

    def has_add_permission(self, request, obj=None):
        return False


# ═══════════════════════════════════════════
# ORDER
# ═══════════════════════════════════════════

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = (
        'reference', 'customer_name', 'customer_email',
        'status_badge', 'item_count', 'total_display', 'created_at',
    )
    list_filter   = ('status', 'created_at', 'shipping_country')
    search_fields = ('reference', 'customer_name', 'customer_email', 'customer_phone')
    readonly_fields = (
        'reference', 'created_at', 'updated_at',
        'shipping_address_display', 'item_count',
    )
    list_per_page = 30
    ordering      = ('-created_at',)
    inlines       = [OrderItemInline]

    fieldsets = (
        ('Order', {
            'fields': ('reference', 'status', 'total', 'notes', 'created_at', 'updated_at'),
        }),
        ('Customer', {
            'fields': ('user', 'customer_name', 'customer_email', 'customer_phone'),
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_name', 'shipping_phone',
                'shipping_line1', 'shipping_line2',
                'shipping_city', 'shipping_state',
                'shipping_postcode', 'shipping_country',
            ),
        }),
    )

    def status_badge(self, obj):
        colours = {
            'pending':   '#b8860b',
            'confirmed': '#2e7d32',
            'shipped':   '#1565c0',
            'delivered': '#4a148c',
            'cancelled': '#c62828',
            'refunded':  '#6d4c41',
        }
        colour = colours.get(obj.status, '#555')
        return format_html(
            '<span style="'
            'background:{};color:#fff;padding:3px 10px;'
            'border-radius:3px;font-size:11px;letter-spacing:0.05em;'
            'text-transform:uppercase;font-weight:500;">{}</span>',
            colour, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def total_display(self, obj):
        return f'£{obj.total:,.2f}'
    total_display.short_description = 'Total'

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


# ═══════════════════════════════════════════
# ORDER ITEM (standalone — useful for exports / searching)
# ═══════════════════════════════════════════

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display  = (
        'order_ref', 'product', 'variant_display',
        'quantity', 'price', 'subtotal_display',
    )
    list_filter   = ('order__status',)
    search_fields = (
        'order__reference', 'product__name',
        'snapshot_variant_name', 'snapshot_size', 'snapshot_sku',
    )
    readonly_fields = (
        'order', 'product', 'variant_size', 'quantity', 'price',
        'snapshot_variant_name', 'snapshot_size', 'snapshot_sku',
    )
    raw_id_fields = ('order', 'product', 'variant_size')

    def order_ref(self, obj):
        return obj.order.reference
    order_ref.short_description = 'Order Ref'

    def variant_display(self, obj):
        return obj.variant_display
    variant_display.short_description = 'Variant / Size'

    def subtotal_display(self, obj):
        return f'£{obj.subtotal:,.2f}'
    subtotal_display.short_description = 'Subtotal'

    def has_add_permission(self, request):
        return False


# ═══════════════════════════════════════════
# CART  (read-only — diagnostic use)
# ═══════════════════════════════════════════

class CartItemInline(admin.TabularInline):
    model           = CartItem
    extra           = 0
    readonly_fields = ('product', 'variant_size', 'quantity', 'unit_price', 'subtotal_display', 'added_at')
    fields          = ('product', 'variant_size', 'quantity', 'unit_price', 'subtotal_display', 'added_at')
    can_delete      = False

    def unit_price(self, obj):
        return f'£{obj.unit_price:,.2f}'
    unit_price.short_description = 'Unit Price'

    def subtotal_display(self, obj):
        return f'£{obj.subtotal:,.2f}'
    subtotal_display.short_description = 'Subtotal'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display  = ('session_key', 'user', 'customer_email', 'is_abandoned', 'item_count', 'created_at')
    list_filter   = ('is_abandoned', 'created_at')
    search_fields = ('session_key', 'user__email', 'customer_email')
    readonly_fields = ('session_key', 'created_at', 'updated_at')
    inlines       = [CartItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

    def has_add_permission(self, request):
        return False
