from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Product, Collection, LookBook
from .views import HOME_CACHE_KEY


@receiver([post_save, post_delete], sender=Product)
def invalidate_home_cache_on_product_change(sender, instance, **kwargs):
    cache.delete(HOME_CACHE_KEY)


@receiver([post_save, post_delete], sender=Collection)
def invalidate_home_cache_on_collection_change(sender, instance, **kwargs):
    cache.delete(HOME_CACHE_KEY)


@receiver([post_save, post_delete], sender=LookBook)
def invalidate_home_cache_on_lookbook_change(sender, instance, **kwargs):
    cache.delete(HOME_CACHE_KEY)