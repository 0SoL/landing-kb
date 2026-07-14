import json

from django.utils.translation import gettext as _


def organization_base():
    """Built per-request so the active language is applied to translatable strings."""
    return {
        '@type': 'Organization',
        'name': 'РЖД-Инфра Казахстан',
        'description': _('Проектирование, строительство и реконструкция железнодорожных путей для промышленных предприятий, портов и логистических терминалов Казахстана.'),
        'areaServed': 'Kazakhstan',
        'serviceType': [
            _('Строительство железнодорожных путей'),
            _('Реконструкция железнодорожных путей'),
            _('Проектирование железнодорожных путей'),
            _('Укладка рельсов'),
        ],
        'address': {
            '@type': 'PostalAddress',
            'addressCountry': 'KZ',
        },
        'contactPoint': {
            '@type': 'ContactPoint',
            'contactType': 'customer service',
            'availableLanguage': ['Russian', 'English'],
        },
    }


def organization_schema(request=None):
    schema = {'@context': 'https://schema.org', **organization_base()}
    if request is not None:
        site_url = request.build_absolute_uri('/')
        schema['url'] = site_url
        schema['@id'] = site_url
    return schema


def faq_schema(items):
    return {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {
                '@type': 'Question',
                'name': item.question,
                'acceptedAnswer': {
                    '@type': 'Answer',
                    'text': item.answer,
                },
            }
            for item in items
        ],
    }


def breadcrumb_schema(request, crumbs):
    """
    crumbs: list of (name, url_path) tuples. Use None for url_path on the last item.
    """
    item_list = []
    for position, (name, path) in enumerate(crumbs, start=1):
        item = {
            '@type': 'ListItem',
            'position': position,
            'name': name,
        }
        if path is not None:
            item['item'] = request.build_absolute_uri(path)
        item_list.append(item)
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': item_list,
    }


def article_schema(article, request=None):
    schema = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': article.title,
        'description': article.excerpt,
        'author': {
            '@type': 'Person',
            'name': article.author or _('Редакция'),
        },
        'datePublished': str(article.published_at),
        'publisher': organization_base(),
    }
    if request is not None and article.cover_image:
        schema['image'] = request.build_absolute_uri(article.cover_image.url)
    if request is not None:
        schema['url'] = request.build_absolute_uri(article.get_absolute_url())
    return schema


def service_schema(service, request=None):
    schema = {
        '@context': 'https://schema.org',
        '@type': 'Service',
        'name': service.title,
        'description': service.short_description,
        'provider': organization_base(),
        'areaServed': 'Kazakhstan',
        'serviceType': service.title,
    }
    if request is not None:
        schema['url'] = request.build_absolute_uri(service.get_absolute_url())
    return schema


def project_schema(project, request=None):
    schema = {
        '@context': 'https://schema.org',
        '@type': 'Project',
        'name': project.title,
        'description': project.task,
        'location': {
            '@type': 'Place',
            'name': project.location,
        },
        'provider': organization_base(),
    }
    if request is not None:
        schema['url'] = request.build_absolute_uri(project.get_absolute_url())
    return schema


def webpage_schema(name, description, request=None, page_type='WebPage'):
    schema = {
        '@context': 'https://schema.org',
        '@type': page_type,
        'name': name,
        'description': description,
        'publisher': organization_base(),
    }
    if request is not None:
        schema['url'] = request.build_absolute_uri()
    return schema


def to_json(schema_or_list):
    """Accepts a single schema dict or a list of schema dicts."""
    return json.dumps(schema_or_list, ensure_ascii=False, indent=2)
