from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('collections/<slug:slug>/', views.collection_detail, name='collection_detail'),
    path('lookbooks/<slug:slug>/', views.lookbook_detail, name='lookbook_detail'),
]