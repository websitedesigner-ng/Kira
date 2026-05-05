from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.store.sitemaps import (
    StaticSitemap,
    ProductSitemap,
    CollectionSitemap,
    LookbookSitemap,
)
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView


sitemaps = {
    'static':      StaticSitemap(),
    'products':    ProductSitemap(),
    'collections': CollectionSitemap(),
    'lookbooks':   LookbookSitemap(),
}

handler400 = 'apps.pages.views.bad_request'
handler403 = 'apps.pages.views.permission_denied'
handler404 = 'apps.pages.views.page_not_found'
handler500 = 'apps.pages.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.store.urls')),
    path('', include('apps.orders.urls')),
    path('account/', include('apps.accounts.urls')),
    path('', include('apps.pages.urls')),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'
    ),
    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='robots.txt',
            content_type='text/plain'
        )
    ),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)