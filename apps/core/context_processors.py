from .models import Announcement, Category


def global_context(request):
    return {
        'announcement': Announcement.objects.filter(is_active=True).first(),
        'categories': Category.objects.all(),
        'cart_count': 0,  # swap with real cart logic when ready
    }