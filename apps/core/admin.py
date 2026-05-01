from django.contrib import admin
from django.utils.html import format_html
from .models import Announcement, Category, Product


# ─── ANNOUNCEMENT ───
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display  = ('message', 'link_text', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_filter   = ('is_active',)


# ─── CATEGORY ───
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'slug', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)


# ─── PRODUCT ───
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'collection', 'category', 'price',
        'badge', 'image_preview',
        'is_featured', 'is_new_arrival', 'is_trending',
        'is_active',
    )
    list_editable = (
        'is_featured', 'is_new_arrival', 'is_trending', 'is_active',
    )
    list_filter   = (
        'is_active', 'is_featured', 'is_new_arrival', 'is_trending',
        'category', 'badge',
    )
    search_fields = ('name', 'collection', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_preview', 'created_at', 'updated_at')

    fieldsets = (
        ('Core Info', {
            'fields': ('name', 'slug', 'collection', 'category', 'description', 'price', 'colors')
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

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;width:48px;object-fit:cover;border-radius:2px;">',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Preview'
