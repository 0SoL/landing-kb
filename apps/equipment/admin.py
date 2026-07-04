from django.contrib import admin
from parler.admin import TranslatableAdmin
from unfold.admin import ModelAdmin
from .models import EquipmentCategory, Equipment


@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']
    fieldsets = [
        ('Основное', {
            'fields': ['name', 'order'],
        }),
    ]


@admin.register(Equipment)
class EquipmentAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ['name', 'category', 'is_published', 'order']
    list_editable = ['is_published', 'order']
    list_filter = ['category', 'is_published']
    search_fields = ['translations__name', 'translations__purpose']
    fieldsets = [
        ('Основное', {
            'fields': ['category', 'name', 'purpose', 'application', 'image'],
        }),
        ('Характеристики', {
            'fields': ['specifications'],
        }),
        ('Настройки', {
            'fields': ['is_published', 'order'],
        }),
    ]
