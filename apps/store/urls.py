from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('collections/', views.collection_list, name='collection_list'),
    path('collections/<slug:slug>/', views.collection_detail, name='collection_detail'),
    path('lookbooks/', views.lookbook_list, name='lookbook_list'),
    path('lookbooks/<slug:slug>/', views.lookbook_detail, name='lookbook_detail'),
]