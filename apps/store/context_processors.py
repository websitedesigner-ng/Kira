from .models import Announcement, Category
from django.conf import settings


def global_context(request):
    return {
        'announcement': Announcement.objects.filter(is_active=True).first(),
        'categories': Category.objects.all(),
        'cart_count': 0,
    }

def analytics(request):
    return {
        'GA4_MEASUREMENT_ID': settings.GA4_MEASUREMENT_ID
    }