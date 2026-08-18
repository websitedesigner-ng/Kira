from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from .models import Product, Category, Collection, LookBook
from django_filters.views import FilterView
from .filters import ProductFilter
from django.core.paginator import Paginator
from django.db import models

HOME_CACHE_KEY = 'home_page_context'


def _build_home_context():
    featured_products = list(Product.objects.filter(is_featured=True, is_active=True)[:4])
    new_arrivals = list(Product.objects.filter(is_new_arrival=True, is_active=True)[:8])
    trending_products = list(Product.objects.filter(is_trending=True, is_active=True)[:4])
    collections = list(Collection.objects.filter(is_active=True).order_by('order')[:3])
    lookbooks = list(LookBook.objects.filter(is_published=True)[:3])

    return {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'trending_products': trending_products,
        'collections': collections,
        'lookbooks': lookbooks,
        'show_featured': bool(featured_products),
        'show_new_arrivals': bool(new_arrivals),
        'show_trending': bool(trending_products),
        'show_collections': bool(collections),
        'show_lookbook': bool(lookbooks),
    }


def home(request):
    context = cache.get(HOME_CACHE_KEY)
    if context is None:
        context = _build_home_context()
        cache.set(HOME_CACHE_KEY, context, timeout=None)  # forever, until signal deletes it

    return render(request, 'home.html', context)



def product_list(request):
    f = ProductFilter(
        request.GET,
        queryset=Product.objects.filter(is_active=True).select_related('category', 'collection').prefetch_related('tags')
    )
    qs = f.qs
    
    tags = request.GET.getlist('tag')
    if tags:
        for tag in tags:
            qs = qs.filter(tags__slug=tag)
        qs = qs.distinct()

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        qs = qs.order_by('price')
    elif sort == 'price_desc':
        qs = qs.order_by('-price')
    elif sort == 'newest':
        qs = qs.order_by('-created_at')

    paginator = Paginator(qs, 9)
    page      = request.GET.get('page')
    products  = paginator.get_page(page)
    
    return render(request, 'store/product_list.html', {
        'filter':            f,
        'products':          products,
        'active_category':   f.form.cleaned_data.get('category') if f.form.is_valid() else None,
        'active_collection': f.form.cleaned_data.get('collection') if f.form.is_valid() else None,
        'active_tags':       request.GET.getlist('tag'),
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