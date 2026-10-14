from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.templatetags.static import static as static_url
from django.views.generic.base import RedirectView
from apps.articles import views as article_views
from apps.core import views as core_views
from apps.seo.sitemaps import StaticViewSitemap, InvestorPagesSitemap, ProjectSitemap, ServiceSitemap, ArticleSitemap
from apps.seo import views as seo_views


def health_check(request):
    """Container liveness probe. Intentionally trivial: no DB, no S3, no
    business logic — just proves the WSGI worker can serve a request."""
    return HttpResponse('OK', content_type='text/plain')

sitemaps = {
    'static': StaticViewSitemap,
    'investors': InvestorPagesSitemap,
    'projects': ProjectSitemap,
    'services': ServiceSitemap,
    'articles': ArticleSitemap,
}

# Non-language-prefixed URLs: health probe, admin, language switcher, SEO files
urlpatterns = [
    path('health/', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', seo_views.robots_txt, name='robots_txt'),
    # Browsers and crawlers probe /favicon.ico at the root regardless of <link> tags
    path('favicon.ico', RedirectView.as_view(
        url=static_url('img/favicon/favicon.ico'), permanent=True,
    )),
    path('llms.txt', seo_views.llms_txt, name='llms_txt'),
]

# All content URLs get /ru/ and /en/ prefixes
urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),
    path('uslugi/', include('apps.services.urls')),
    path('proekty/', include('apps.projects.urls')),
    path('tekhnika/', include('apps.equipment.urls')),
    path('novosti/', include('apps.articles.urls', namespace='articles')),
    path('investoram/', article_views.article_list, {'category_slug': 'investoram'}, name='investor_list'),
    path('tekhnicheskaya-informatsiya/', article_views.article_list, {'category_slug': 'tekhnicheskaya-informatsiya'}, name='tech_list'),
    path('direktoru-kniga/', core_views.director_book, name='book_list'),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
