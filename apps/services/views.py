from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _
from .models import Service, ServiceCategory
from apps.seo.jsonld import service_schema, breadcrumb_schema, webpage_schema, to_json


def service_list(request):
    categories = ServiceCategory.objects.prefetch_related('services').filter(services__is_published=True).distinct().order_by('order')
    meta_title = _('Услуги по строительству железных дорог')
    meta_description = _('Полный цикл работ: проектирование, строительство, реконструкция и консалтинг в сфере железнодорожной инфраструктуры.')
    crumbs = [
        (_('Главная'), reverse('core:home')),
        (_('Услуги'), None),
    ]
    schemas = [
        webpage_schema(meta_title, meta_description, request, page_type='CollectionPage'),
        breadcrumb_schema(request, crumbs),
    ]
    context = {
        'categories': categories,
        'meta_title': meta_title,
        'meta_description': meta_description,
        'schema_json': to_json(schemas),
    }
    return render(request, 'services/list.html', context)


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_published=True)
    crumbs = [
        (_('Главная'), reverse('core:home')),
        (_('Услуги'), reverse('services:list')),
        (service.title, None),
    ]
    schemas = [
        service_schema(service, request),
        breadcrumb_schema(request, crumbs),
    ]
    context = {
        'service': service,
        'meta_title': service.meta_title or service.title,
        'meta_description': service.meta_description or service.short_description,
        'schema_json': to_json(schemas),
        'og_image': request.build_absolute_uri(service.cover_image.url) if service.cover_image else None,
    }
    return render(request, 'services/detail.html', context)
