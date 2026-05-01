from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Announcement, Category, Collection, Tag,
    Product, ProductVariant, ProductDimension, ProductDetail, ProductImage,
    LookBook, LookBookImage,
)


# ─── ANNOUNCEMENT ───
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display  = ('message', 'link_text', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_filter   = ('is_active',)


# ─── CATEGORY ───
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ('name', 'slug', 'order')
    list_editable       = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    ordering            = ('order',)


# ─── COLLECTION ───
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display        = ('name', 'slug', 'order', 'is_active', 'is_featured', 'created_at')
    list_editable       = ('order', 'is_active', 'is_featured')
    list_filter         = ('is_active', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    search_fields       = ('name',)


# ─── TAG ───
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display        = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields       = ('name',)


# ─── PRODUCT INLINES ───
class ProductVariantInline(admin.TabularInline):
    model  = ProductVariant
    extra  = 1
    fields = ('size', 'color', 'sku', 'stock', 'price_override', 'is_active')


class ProductImageInline(admin.TabularInline):
    model          = ProductImage
    extra          = 1
    fields         = ('image', 'alt_text', 'position', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;width:48px;object-fit:cover;border-radius:2px;">',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Preview'


class ProductDetailInline(admin.TabularInline):
    model  = ProductDetail
    extra  = 1
    fields = ('title', 'value', 'position')


class ProductDimensionInline(admin.StackedInline):
    model = ProductDimension
    extra = 0


# ─── PRODUCT ───
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'collection', 'category', 'price',
        'badge', 'image_preview',
        'is_featured', 'is_new_arrival', 'is_trending', 'is_active',
    )
    list_editable   = ('is_featured', 'is_new_arrival', 'is_trending', 'is_active')
    list_filter     = (
        'is_active', 'is_featured', 'is_new_arrival', 'is_trending',
        'category', 'collection', 'badge',
    )
    search_fields   = ('name', 'description', 'collection__name', 'tags__name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    filter_horizontal = ('tags',)

    fieldsets = (
        ('Core Info', {
            'fields': ('name', 'slug', 'collection', 'category', 'description', 'price', 'tags')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Badge', {
            'fields': ('badge',)
        }),
        ('Homepage Sections', {
            'fields': ('is_featured', 'is_new_arrival', 'is_trending'),
            'description': 'Controls which section this product appears in on the home page.'
        }),
        ('Visibility', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [ProductVariantInline, ProductImageInline, ProductDetailInline, ProductDimensionInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;width:48px;object-fit:cover;border-radius:2px;">',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Preview'


# ─── LOOKBOOK ───
class LookBookImageInline(admin.TabularInline):
    model  = LookBookImage
    extra  = 1
    fields = ('image', 'caption', 'position')


@admin.register(LookBook)
class LookBookAdmin(admin.ModelAdmin):
    list_display        = ('title', 'season', 'is_published', 'created_at')
    list_editable       = ('is_published',)
    list_filter         = ('is_published', 'season')
    prepopulated_fields = {'slug': ('title',)}
    search_fields       = ('title', 'season')
    inlines             = [LookBookImageInline]