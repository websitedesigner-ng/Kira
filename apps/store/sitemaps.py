# ─────────────────────────────────────────────────────────────
# apps/store/sitemaps.py
# ─────────────────────────────────────────────────────────────

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, Collection, LookBook


# ── Static pages ─────────────────────────────────────────────
class StaticSitemap(Sitemap):
    changefreq = 'monthly'
    protocol   = 'https'

    pages = [
        ('store:home',             1.0),
        ('store:product_list',     0.9),
        ('store:collection_list',  0.8),
        ('store:lookbook_list',    0.7),
        ('pages:our_story',        0.6),
        ('pages:savoir_faire',     0.6),
        ('pages:sustainability',   0.6),
        ('pages:contact',          0.5),
        ('pages:faqs',             0.5),
        ('pages:book_appointment', 0.5),
        ('pages:size_guide',       0.4),
        ('pages:shipping_returns', 0.4),
        ('pages:privacy_policy',   0.3),
        ('pages:terms',            0.3),
    ]

    def items(self):
        return self.pages

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]


# ── Products ──────────────────────────────────────────────────
class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority   = 0.85
    protocol   = 'https'

    def items(self):
        # is_active ✓  |  updated_at ✓ (auto_now=True)
        return Product.objects.filter(is_active=True).select_related('collection')

    def location(self, obj):
        return reverse('store:product_detail', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.updated_at


# ── Collections ───────────────────────────────────────────────
class CollectionSitemap(Sitemap):
    changefreq = 'monthly'
    priority   = 0.75
    protocol   = 'https'

    def items(self):
        # is_active ✓  |  no updated_at → use created_at
        return Collection.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('store:collection_detail', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.created_at


# ── Lookbooks ─────────────────────────────────────────────────
class LookbookSitemap(Sitemap):
    changefreq = 'monthly'
    priority   = 0.65
    protocol   = 'https'

    def items(self):
        # is_published ✓ (not is_active)  |  no updated_at → use created_at
        return LookBook.objects.filter(is_published=True)

    def location(self, obj):
        return reverse('store:lookbook_detail', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.created_at
