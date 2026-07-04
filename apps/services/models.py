from django.db import models
from django.urls import reverse
from parler.models import TranslatableModel, TranslatedFields


class ServiceCategory(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=100, verbose_name='Название'),
    )
    slug = models.SlugField(unique=True, verbose_name='URL')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Иконка (SVG name)')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        ordering = ['order']
        verbose_name = 'Категория услуг'
        verbose_name_plural = 'Категории услуг'

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or f'Категория #{self.pk}'


class Service(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name='Название'),
        short_description=models.TextField(max_length=300, verbose_name='Краткое описание'),
        full_description=models.TextField(verbose_name='Полное описание'),
        tasks_solved=models.TextField(blank=True, verbose_name='Задачи которые решает', help_text='Каждая задача с новой строки'),
        stages=models.JSONField(default=list, verbose_name='Этапы', help_text='[{"title": "...", "description": "..."}]'),
        duration=models.CharField(max_length=100, blank=True, verbose_name='Средняя продолжительность'),
        client_result=models.TextField(blank=True, verbose_name='Что получает заказчик'),
        meta_title=models.CharField(max_length=70, blank=True, verbose_name='Meta Title'),
        meta_description=models.CharField(max_length=160, blank=True, verbose_name='Meta Description'),
    )

    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', verbose_name='Категория')
    slug = models.SlugField(unique=True, verbose_name='URL')
    cover_image = models.ImageField(upload_to='services/', blank=True, verbose_name='Обложка')
    is_published = models.BooleanField(default=True, verbose_name='Опубликована')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        ordering = ['order']
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True) or f'Услуга #{self.pk}'

    def get_absolute_url(self):
        return reverse('services:detail', kwargs={'slug': self.slug})

    def get_tasks_list(self):
        return [t.strip() for t in self.tasks_solved.splitlines() if t.strip()]
