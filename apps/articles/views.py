from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import Article, ArticleCategory
from apps.seo.jsonld import article_schema, breadcrumb_schema, to_json

CATEGORY_META = {
    'novosti': {
        'title': 'Новости — РЖД-Инфра Казахстан',
        'description': 'Последние новости компании: завершённые проекты, отраслевые события и обновления.',
    },
    'investoram': {
        'title': 'Инвесторам — РЖД-Инфра Казахстан',
        'description': 'Информация для инвесторов: финансовые показатели, перспективы развития железнодорожной инфраструктуры Казахстана.',
    },
    'tekhnicheskaya-informatsiya': {
        'title': 'Техническая информация — РЖД-Инфра Казахстан',
        'description': 'Технические статьи о строительстве и реконструкции железнодорожных путей, нормативная база, стандарты.',
    },
    'direktoru-kniga': {
        'title': 'Книга директора — РЖД-Инфра Казахстан',
        'description': 'Аналитические материалы и статьи от руководства компании.',
    },
}


def article_list(request, category_slug):
    category = get_object_or_404(ArticleCategory, slug=category_slug)
    articles = Article.objects.filter(category=category, is_published=True)
    meta = CATEGORY_META.get(category_slug, {'title': category.name, 'description': ''})
    context = {
        'category': category,
        'articles': articles,
        'meta_title': meta['title'],
        'meta_description': meta['description'],
    }
    return render(request, 'articles/list.html', context)


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    crumbs = [
        ('Главная', reverse('core:home')),
        (article.category.name, reverse('articles:news_list')),
        (article.title, None),
    ]
    schemas = [
        article_schema(article, request),
        breadcrumb_schema(request, crumbs),
    ]
    context = {
        'article': article,
        'meta_title': article.meta_title or article.title,
        'meta_description': article.meta_description or article.excerpt,
        'schema_json': to_json(schemas),
        'og_image': request.build_absolute_uri(article.cover_image.url) if article.cover_image else None,
    }
    return render(request, 'articles/detail.html', context)
