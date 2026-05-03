import django_filters
from django.db import models
from .models import Product, Category, Collection



class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='search', label='Search')

    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name="category",
        to_field_name="slug"
    )

    collection = django_filters.ModelChoiceFilter(
        queryset=Collection.objects.filter(is_active=True),
        field_name="collection",
        to_field_name="slug"
    )

    badge = django_filters.ChoiceFilter(choices=Product.BADGE_CHOICES)

    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    new_arrival = django_filters.BooleanFilter(field_name='is_new_arrival')
    featured = django_filters.BooleanFilter(field_name='is_featured')

    def search(self, queryset, name, value):
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(collection__name__icontains=value) |
            models.Q(category__name__icontains=value)
        ).distinct()

    class Meta:
        model = Product
        fields = ['q', 'category', 'collection', 'badge', 'min_price', 'max_price']
