from django.contrib import admin
from parler.admin import TranslatableAdmin
from unfold.admin import ModelAdmin, TabularInline
from .models import Project, ProjectImage


class ProjectImageInline(TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'alt_text', 'order']


@admin.register(Project)
class ProjectAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ['title', 'client_type', 'year', 'location', 'is_featured', 'is_published', 'order']
    list_editable = ['is_featured', 'is_published', 'order']
    list_filter = ['client_type', 'is_published', 'is_featured', 'year']
    search_fields = ['translations__title', 'client', 'translations__location']
    inlines = [ProjectImageInline]
    fieldsets = [
        ('Основное', {
            'fields': ['title', 'slug', 'client', 'client_type', 'year', 'cover_image'],
        }),
        ('Описание проекта', {
            'fields': ['task', 'solution', 'result'],
        }),
        ('Локация и бюджет', {
            'fields': ['location', 'budget_display'],
        }),
        ('Параметры', {
            'fields': ['track_length_km', 'switches_count', 'duration_months'],
        }),
        ('SEO', {
            'fields': ['meta_title', 'meta_description'],
            'classes': ['collapse'],
        }),
        ('Настройки', {
            'fields': ['is_featured', 'is_published', 'order'],
        }),
    ]
