from django.contrib import admin
from parler.admin import TranslatableAdmin
from unfold.admin import ModelAdmin
from .models import CompanyStats, FAQItem, ContactInquiry


@admin.register(CompanyStats)
class CompanyStatsAdmin(ModelAdmin):
    def has_add_permission(self, request):
        return not CompanyStats.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FAQItem)
class FAQItemAdmin(TranslatableAdmin, ModelAdmin):
    list_display = ['question', 'order', 'is_published']
    list_editable = ['order', 'is_published']
    search_fields = ['translations__question', 'translations__answer']
    fieldsets = [
        ('Основное', {
            'fields': ['question', 'answer', 'order', 'is_published'],
        }),
    ]


@admin.register(ContactInquiry)
class ContactInquiryAdmin(ModelAdmin):
    list_display = ['name', 'company', 'phone', 'email', 'created_at', 'is_processed']
    list_filter = ['is_processed']
    list_editable = ['is_processed']
    readonly_fields = ['name', 'company', 'phone', 'email', 'message', 'created_at']
    actions = ['mark_processed']

    def mark_processed(self, request, queryset):
        queryset.update(is_processed=True)
    mark_processed.short_description = 'Отметить как обработанные'

    def has_add_permission(self, request):
        return False
