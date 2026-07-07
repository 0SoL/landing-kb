from django.contrib import admin
from parler.admin import TranslatableAdmin
from unfold.admin import ModelAdmin
from .models import Equipment


@admin.register(Equipment)
class EquipmentAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ['name', 'is_published', 'order']
    list_editable = ['is_published', 'order']
    list_filter = ['is_published']
    search_fields = ['translations__name', 'translations__purpose']
    fieldsets = [
        ('Основное', {
            'fields': ['name', 'purpose', 'application', 'image'],
        }),
        ('Характеристики', {
            'fields': ['specifications'],
        }),
        ('Настройки', {
            'fields': ['is_published', 'order'],
        }),
    ]
