from django.contrib import admin
from parler.admin import TranslatableAdmin
from unfold.admin import ModelAdmin
from .models import ServiceCategory, Service


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ['name', 'slug', 'order']
    list_editable = ['order']
    fieldsets = [
        ('Основное', {
            'fields': ['name', 'slug', 'icon', 'order'],
        }),
    ]


@admin.register(Service)
class ServiceAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'order']
    list_editable = ['is_published', 'order']
    list_filter = ['category', 'is_published']
    search_fields = ['translations__title', 'translations__short_description']
    fieldsets = [
        ('Основное', {
            'fields': ['category', 'title', 'slug', 'short_description', 'full_description', 'cover_image'],
        }),
        ('Детали', {
            'fields': ['tasks_solved', 'stages', 'duration', 'client_result'],
        }),
        ('SEO', {
            'fields': ['meta_title', 'meta_description'],
            'classes': ['collapse'],
        }),
        ('Настройки', {
            'fields': ['is_published', 'order'],
        }),
    ]
