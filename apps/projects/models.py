from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class Project(TranslatableModel):
    CLIENT_TYPES = [
        ('port', _('Порт')),
        ('factory', _('Завод')),
        ('terminal', _('Терминал')),
        ('logistics', _('Логистический центр')),
        ('other', _('Другое')),
    ]

    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name='Название'),
        task=models.TextField(verbose_name='Задача клиента'),
        solution=models.TextField(verbose_name='Наше решение'),
        result=models.TextField(verbose_name='Результат'),
        location=models.CharField(max_length=200, blank=True, verbose_name='Локация'),
        budget_display=models.CharField(max_length=100, blank=True, verbose_name='Бюджет (отображение)', help_text='Например: от 150 млн тг'),
        meta_title=models.CharField(max_length=70, blank=True, verbose_name='Meta Title'),
        meta_description=models.CharField(max_length=160, blank=True, verbose_name='Meta Description'),
    )

    slug = models.SlugField(unique=True, verbose_name='URL')
    client = models.CharField(max_length=200, blank=True, verbose_name='Клиент')
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPES, verbose_name='Тип клиента')
    year = models.PositiveIntegerField(verbose_name='Год')

    track_length_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Длина пути (км)')
    switches_count = models.PositiveIntegerField(null=True, blank=True, verbose_name='Стрелочных переводов')
    duration_months = models.PositiveIntegerField(null=True, blank=True, verbose_name='Продолжительность (мес.)')

    cover_image = models.ImageField(upload_to='projects/covers/', verbose_name='Обложка')

    is_featured = models.BooleanField(default=False, verbose_name='На главной')
    is_published = models.BooleanField(default=True, verbose_name='Опубликован')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        ordering = ['-year', 'order']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True) or f'Проект #{self.pk}'

    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'slug': self.slug})

    def get_client_type_display_ru(self):
        return dict(self.CLIENT_TYPES).get(self.client_type, '')


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images', verbose_name='Проект')
    image = models.ImageField(upload_to='projects/gallery/', verbose_name='Изображение')
    alt_text = models.CharField(max_length=300, blank=True, verbose_name='Alt текст')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        ordering = ['order']
        verbose_name = 'Фото проекта'
        verbose_name_plural = 'Фото проекта'

    def __str__(self):
        title = self.project.safe_translation_getter('title', any_language=True) or f'#{self.project_id}'
        return f'Фото: {title}'
