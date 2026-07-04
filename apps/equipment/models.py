from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class EquipmentCategory(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=100, verbose_name='Название'),
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        ordering = ['order']
        verbose_name = 'Категория техники'
        verbose_name_plural = 'Категории техники'

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or f'Категория #{self.pk}'


class Equipment(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200, verbose_name='Название'),
        purpose=models.TextField(verbose_name='Назначение'),
        application=models.TextField(blank=True, verbose_name='Где применяется'),
    )

    category = models.ForeignKey(EquipmentCategory, on_delete=models.CASCADE, related_name='items', verbose_name='Категория')
    specifications = models.JSONField(default=dict, verbose_name='Технические характеристики', help_text='{"Грузоподъемность": "25т"}')
    image = models.ImageField(upload_to='equipment/', blank=True, verbose_name='Фото')
    is_published = models.BooleanField(default=True, verbose_name='Опубликована')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        ordering = ['order']
        verbose_name = 'Техника'
        verbose_name_plural = 'Техника'

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or f'Техника #{self.pk}'
