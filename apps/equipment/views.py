from django.shortcuts import render
from .models import EquipmentCategory


def equipment_list(request):
    categories = EquipmentCategory.objects.prefetch_related('items').filter(items__is_published=True).distinct().order_by('order')
    context = {
        'categories': categories,
        'meta_title': 'Парк техники — РЖД-Инфра Казахстан',
        'meta_description': 'Собственный парк специализированной железнодорожной техники: путеукладчики, рельсоукладчики, балластировочные машины.',
    }
    return render(request, 'equipment/list.html', context)
