from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from .models import Equipment
from apps.seo.jsonld import webpage_schema, breadcrumb_schema, to_json


def equipment_list(request):
    equipment = Equipment.objects.filter(is_published=True).order_by('order')
    meta_title = _('Парк техники')
    meta_description = _('Собственный парк специализированной железнодорожной техники: путеукладчики, рельсоукладчики, балластировочные машины.')
    crumbs = [
        (_('Главная'), reverse('core:home')),
        (_('Техника'), None),
    ]
    schemas = [
        webpage_schema(meta_title, meta_description, request, page_type='CollectionPage'),
        breadcrumb_schema(request, crumbs),
    ]
    context = {
        'equipment': equipment,
        'meta_title': meta_title,
        'meta_description': meta_description,
        'schema_json': to_json(schemas),
    }
    return render(request, 'equipment/list.html', context)
