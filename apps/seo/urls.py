from django.contrib.sitemaps.views import sitemap
from django.urls import path
from .sitemaps import StaticViewSitemap, ProjectSitemap, ServiceSitemap, ArticleSitemap
from . import views

sitemaps = {
    'static': StaticViewSitemap,
    'projects': ProjectSitemap,
    'services': ServiceSitemap,
    'articles': ArticleSitemap,
}

urlpatterns = [
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap',
    ),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]
