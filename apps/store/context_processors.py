# apps/store/context_processors.py

from .models import Announcement, Category
from django.conf import settings
from apps.orders.cart import SessionCart


def global_context(request):
    try:
        return {
            'announcement': Announcement.objects.filter(is_active=True).first(),
            'categories':   Category.objects.all(),
        }
    except Exception:
        return {
            'announcement': None,
            'categories':   [],
        }


def analytics(request):
    return {
        'GA4_MEASUREMENT_ID': getattr(settings, 'GA4_MEASUREMENT_ID', None)
    }


def cart(request):
    if not hasattr(request, 'session'):
        return {'cart_count': 0}
    try:
        cart = SessionCart(request)
        return {'cart_count': cart.get_count()}
    except Exception:
        return {'cart_count': 0}