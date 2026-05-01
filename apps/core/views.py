from django.shortcuts import render, get_object_or_404
from .models import Product, Category


def home(request):
    context = {
        'featured_products': Product.objects.filter(is_featured=True,    is_active=True),
        'new_arrivals':      Product.objects.filter(is_new_arrival=True,  is_active=True),
        'trending_products': Product.objects.filter(is_trending=True,     is_active=True),
    }
    return render(request, 'home.html', context)


def product_list(request):
    products = Product.objects.filter(is_active=True)

    category_slug = request.GET.get('category')
    active_category = None

    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    context = {
        'products': products,
        'active_category': active_category,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    related = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related,
    }
    return render(request, 'store/product_detail.html', context)
