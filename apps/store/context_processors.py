from .models import Announcement, Category
from django.conf import settings
from apps.orders.cart import SessionCart


def global_context(request):
    return {
        'announcement': Announcement.objects.filter(is_active=True).first(),
        'categories': Category.objects.all(),
    }

def analytics(request):
    return {
        'GA4_MEASUREMENT_ID': settings.GA4_MEASUREMENT_ID
    }


def cart(request):
    cart = SessionCart(request)
    return {'cart_count': cart.get_count()}