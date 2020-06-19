from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from blog.sitemaps import PostSitemap

sitemaps = {
    'posts' : PostSitemap
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps' : sitemaps}, \
            name='django.contrib.sitemaps.views.sitemap' ),
    path('', include('blog.urls', namespace='blog')),
]
