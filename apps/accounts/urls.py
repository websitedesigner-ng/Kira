from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ─── AUTH ───
    path('login/',    views.login_view,  name='login'),
    path('signup/',   views.signup_view, name='signup'),
    path('logout/',   views.logout_view, name='logout'),

    # ─── ACCOUNT ───
    path('',         views.dashboard, name='dashboard'),
    path('profile/', views.profile,   name='profile'),

    # ─── ORDERS ───
    path('orders/',                     views.order_history, name='order_history'),
    path('orders/<str:reference>/',     views.order_detail,  name='order_detail'),

    # ─── ADDRESSES ───
    path('addresses/',                  views.addresses,           name='addresses'),
    path('addresses/add/',              views.address_add,         name='address_add'),
    path('addresses/<int:pk>/edit/', views.address_edit, name='address_edit'),
    path('addresses/<int:pk>/delete/',  views.address_delete,      name='address_delete'),
    path('addresses/<int:pk>/default/', views.address_set_default, name='address_set_default'),
]