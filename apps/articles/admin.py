from django.contrib import admin
from parler.admin import TranslatableAdmin
from unfold.admin import ModelAdmin
from .models import ArticleCategory, Article


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ['name', 'slug', 'order']
    list_editable = ['order']
    fieldsets = [
        ('Основное', {
            'fields': ['name', 'slug', 'order'],
        }),
    ]


@admin.register(Article)
class ArticleAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ['title', 'category', 'published_at', 'is_featured', 'is_published']
    list_editable = ['is_featured', 'is_published']
    list_filter = ['category', 'is_published', 'is_featured']
    search_fields = ['translations__title', 'translations__excerpt']
    fieldsets = [
        ('Основное', {
            'fields': ['category', 'title', 'slug', 'excerpt', 'content', 'cover_image', 'author', 'published_at'],
        }),
        ('SEO', {
            'fields': ['meta_title', 'meta_description'],
            'classes': ['collapse'],
        }),
        ('Настройки', {
            'fields': ['is_featured', 'is_published'],
        }),
    ]
