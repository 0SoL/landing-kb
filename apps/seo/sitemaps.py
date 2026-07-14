from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.projects.models import Project
from apps.services.models import Service
from apps.articles.models import Article


# url name → sitemap priority (homepage 1.0, key sections 0.9, the rest 0.7)
STATIC_VIEW_PRIORITIES = {
    'core:home': 1.0,
    'services:list': 0.9,
    'projects:list': 0.9,
    'equipment:list': 0.9,
    'core:about': 0.7,
    'core:faq': 0.7,
    'core:contacts': 0.7,
    'core:investors': 0.7,
    'core:construction_recommendations': 0.7,
    'core:our_people': 0.7,
    'core:our_leaders': 0.7,
    'articles:news_list': 0.7,
    'investor_list': 0.7,
    'tech_list': 0.7,
    'book_list': 0.7,
}


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'

    def items(self):
        return list(STATIC_VIEW_PRIORITIES.keys())

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return STATIC_VIEW_PRIORITIES[item]


class InvestorPagesSitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        from apps.core.views import INVESTOR_PAGES
        return list(INVESTOR_PAGES.keys())

    def location(self, item):
        return reverse('core:investor_page', kwargs={'slug': item})


class ProjectSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return Project.objects.filter(is_published=True)

    def lastmod(self, obj):
        return None


class ServiceSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return Service.objects.filter(is_published=True)


class ArticleSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.published_at
