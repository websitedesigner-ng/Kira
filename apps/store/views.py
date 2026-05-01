from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Collection, LookBook


def home(request):
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:4]
    new_arrivals = Product.objects.filter(is_new_arrival=True, is_active=True)[:8]
    trending_products = Product.objects.filter(is_trending=True, is_active=True)[:4]
    collections = Collection.objects.filter(is_active=True).order_by('order')[:3]
    lookbooks = LookBook.objects.filter(is_published=True)[:3]

    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'trending_products': trending_products,
        'collections': collections,
        'lookbooks': lookbooks,
        'show_featured': featured_products.exists(),
        'show_new_arrivals': new_arrivals.exists(),
        'show_trending': trending_products.exists(),
        'show_collections': collections.exists(),
        'show_lookbook': lookbooks.exists(),
    }
    return render(request, 'home.html', context)


def product_list(request):
    products = Product.objects.filter(is_active=True)
    category_slug   = request.GET.get('category')
    active_category = None

    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    return render(request, 'store/product_list.html', {
        'products': products,
        'active_category': active_category,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related,
    })


def collection_detail(request, slug):
    collection = get_object_or_404(Collection, slug=slug, is_active=True)
    products   = collection.products.filter(is_active=True)

    return render(request, 'store/collection_detail.html', {
        'collection': collection,
        'products':   products,
    })


def lookbook_detail(request, slug):
    lookbook = get_object_or_404(LookBook, slug=slug, is_published=True)

    return render(request, 'store/lookbook_detail.html', {
        'lookbook': lookbook,
        'images':   lookbook.images.all(),
    })