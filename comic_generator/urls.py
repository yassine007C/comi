from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.sitemaps.views import sitemap
from yourapp.sitemap import accounts, generator



sitemaps = {
    'generator': GeneratedImage,
    'accounts': UserProfile,
    
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('tokens/', include('tokens.urls')),
    path('generator/', include('generator.urls')),
    path('', lambda request: redirect('accounts:login')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
