from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from .models import Article, ArticleCategory
from apps.seo.jsonld import article_schema, breadcrumb_schema, webpage_schema, to_json

CATEGORY_META = {
    'novosti': {
        'title': gettext_lazy('Новости'),
        'description': gettext_lazy('Последние новости компании: завершённые проекты, отраслевые события и обновления.'),
        'hero_sub': gettext_lazy('Завершённые проекты, отраслевые события и обновления компании'),
    },
    'investoram': {
        'title': gettext_lazy('Инвесторам'),
        'description': gettext_lazy('Информация для инвесторов: финансовые показатели, перспективы развития железнодорожной инфраструктуры Казахстана.'),
        'hero_sub': gettext_lazy('Материалы о строительстве подъездных железнодорожных путей для инвесторов'),
    },
    'tekhnicheskaya-informatsiya': {
        'title': gettext_lazy('Техническая информация'),
        'description': gettext_lazy('Технические статьи о строительстве и реконструкции железнодорожных путей, нормативная база, стандарты.'),
        'hero_sub': gettext_lazy('Технические статьи, нормативная база и стандарты'),
    },
    'direktoru-kniga': {
        'title': gettext_lazy('Книга директора'),
        'description': gettext_lazy('Аналитические материалы и статьи от руководства компании.'),
        'hero_sub': gettext_lazy('Аналитические материалы и статьи от руководства компании'),
    },
}


def article_list(request, category_slug):
    category = get_object_or_404(ArticleCategory, slug=category_slug)
    articles = Article.objects.filter(category=category, is_published=True)
    meta = CATEGORY_META.get(category_slug, {'title': category.name, 'description': ''})
    meta_title = str(meta['title'])
    meta_description = str(meta['description'])
    crumbs = [
        (_('Главная'), reverse('core:home')),
        (category.name, None),
    ]
    schemas = [
        webpage_schema(meta_title, meta_description, request, page_type='CollectionPage'),
        breadcrumb_schema(request, crumbs),
    ]
    context = {
        'category': category,
        'articles': articles,
        'meta_title': meta_title,
        'meta_description': meta_description,
        'hero_sub': meta.get('hero_sub', ''),
        'schema_json': to_json(schemas),
    }
    return render(request, 'articles/list.html', context)


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    crumbs = [
        (_('Главная'), reverse('core:home')),
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
        'og_type': 'article',
    }
    return render(request, 'articles/detail.html', context)
