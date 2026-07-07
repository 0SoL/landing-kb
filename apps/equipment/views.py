from django.shortcuts import render
from .models import Equipment


def equipment_list(request):
    equipment = Equipment.objects.filter(is_published=True).order_by('order')
    context = {
        'equipment': equipment,
        'meta_title': 'Парк техники — РЖД-Инфра Казахстан',
        'meta_description': 'Собственный парк специализированной железнодорожной техники: путеукладчики, рельсоукладчики, балластировочные машины.',
    }
    return render(request, 'equipment/list.html', context)
