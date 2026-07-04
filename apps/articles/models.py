from django.db import models
from django.urls import reverse
from parler.models import TranslatableModel, TranslatedFields


class ArticleCategory(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=100, verbose_name='Название'),
    )
    slug = models.SlugField(unique=True, verbose_name='URL')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        ordering = ['order']
        verbose_name = 'Категория статей'
        verbose_name_plural = 'Категории статей'

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or f'Категория #{self.pk}'


class Article(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=250, verbose_name='Заголовок'),
        excerpt=models.TextField(max_length=350, verbose_name='Анонс'),
        content=models.TextField(verbose_name='Содержание (HTML)'),
        meta_title=models.CharField(max_length=70, blank=True, verbose_name='Meta Title'),
        meta_description=models.CharField(max_length=160, blank=True, verbose_name='Meta Description'),
    )

    category = models.ForeignKey(ArticleCategory, on_delete=models.CASCADE, related_name='articles', verbose_name='Категория')
    slug = models.SlugField(unique=True, verbose_name='URL')
    cover_image = models.ImageField(upload_to='articles/', blank=True, verbose_name='Обложка')
    author = models.CharField(max_length=100, blank=True, verbose_name='Автор')
    published_at = models.DateField(verbose_name='Дата публикации')
    is_published = models.BooleanField(default=True, verbose_name='Опубликована')
    is_featured = models.BooleanField(default=False, verbose_name='Главная')

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True) or f'Статья #{self.pk}'

    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'slug': self.slug})
