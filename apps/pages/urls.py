from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('our-story/',          views.our_story,         name='our_story'),
    path('savoir-faire/',       views.savoir_faire,      name='savoir_faire'),
    path('contact/',            views.contact,           name='contact'),
    path('contact/submit/',     views.contact_submit,    name='contact_submit'),
    path('shipping-returns/',   views.shipping_returns,  name='shipping_returns'),
    path('faqs/',               views.faqs,              name='faqs'),
    path('book-appointment/',   views.book_appointment,  name='book_appointment'),
    path('book-appointment/submit/', views.book_appointment_submit, name='book_appointment_submit'),
    path('sustainability/',     views.sustainability,    name='sustainability'),
    path('size-guide/',         views.size_guide,        name='size_guide'),
    path('privacy-policy/',     views.privacy_policy,    name='privacy_policy'),
    path('terms/',              views.terms,             name='terms'),
]