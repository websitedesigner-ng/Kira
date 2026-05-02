from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Collection, LookBook
from django_filters.views import FilterView
from .filters import ProductFilter
from django.core.paginator import Paginator
from django.db import models


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
    f = ProductFilter(
        request.GET,
        queryset=Product.objects.filter(is_active=True).select_related('category', 'collection')
    )
    qs = f.qs

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        qs = qs.order_by('price')
    elif sort == 'price_desc':
        qs = qs.order_by('-price')
    elif sort == 'newest':
        qs = qs.order_by('-created_at')

    paginator = Paginator(qs, 8)
    page      = request.GET.get('page')
    products  = paginator.get_page(page)

    return render(request, 'store/product_list.html', {
        'filter':          f,
        'products':        products,
        'active_category': f.form.cleaned_data.get('category') if f.form.is_valid() else None,
    })



def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # related by same collection first, fall back to category
    related = Product.objects.filter(
        is_active=True
    ).exclude(id=product.id).filter(
        models.Q(collection=product.collection) |
        models.Q(category=product.category)
    ).distinct()[:4]

    return render(request, 'store/product_detail.html', {
        'product':         product,
        'related_products': related,
    })



def collection_list(request):
    paginator   = Paginator(Collection.objects.filter(is_active=True).order_by('order'), 9)
    page        = request.GET.get('page')
    collections = paginator.get_page(page)

    return render(request, 'store/collection_list.html', {
        'collections': collections,
    })

    

def collection_detail(request, slug):
    collection       = get_object_or_404(Collection, slug=slug, is_active=True)
    products         = collection.products.filter(is_active=True)
    other_collections = Collection.objects.filter(
        is_active=True
    ).exclude(id=collection.id).order_by('order')[:3]

    return render(request, 'store/collection_detail.html', {
        'collection':        collection,
        'products':          products,
        'other_collections': other_collections,
    })



def lookbook_list(request):
    paginator = Paginator(LookBook.objects.filter(is_published=True), 9)
    page      = request.GET.get('page')
    lookbooks = paginator.get_page(page)

    return render(request, 'store/lookbook_list.html', {
        'lookbooks': lookbooks,
    })



def lookbook_detail(request, slug):
    lookbook = get_object_or_404(LookBook, slug=slug, is_published=True)
    other_lookbooks = LookBook.objects.filter(
        is_published=True
    ).exclude(id=lookbook.id).order_by('-created_at')[:3]

    return render(request, 'store/lookbook_detail.html', {
        'lookbook':        lookbook,
        'images':          lookbook.images.all(),
        'other_lookbooks': other_lookbooks,
    })