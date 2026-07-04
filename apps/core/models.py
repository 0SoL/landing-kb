from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class CompanyStats(models.Model):
    projects_count = models.PositiveIntegerField(default=0, verbose_name='Проектов выполнено')
    track_km = models.PositiveIntegerField(default=0, verbose_name='Км пути уложено')
    years_on_market = models.PositiveIntegerField(default=0, verbose_name='Лет на рынке')
    employees_count = models.PositiveIntegerField(default=0, verbose_name='Сотрудников')

    class Meta:
        verbose_name = 'Показатели компании'
        verbose_name_plural = 'Показатели компании'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Показатели компании'


class FAQItem(TranslatableModel):
    translations = TranslatedFields(
        question=models.CharField(max_length=500, verbose_name='Вопрос'),
        answer=models.TextField(verbose_name='Ответ'),
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    is_published = models.BooleanField(default=True, verbose_name='Опубликован')

    class Meta:
        ordering = ['order']
        verbose_name = 'FAQ вопрос'
        verbose_name_plural = 'FAQ вопросы'

    def __str__(self):
        return self.safe_translation_getter('question', any_language=True) or f'FAQ #{self.pk}'


class ContactInquiry(models.Model):
    name = models.CharField(max_length=200, verbose_name='Имя')
    company = models.CharField(max_length=200, blank=True, verbose_name='Компания')
    phone = models.CharField(max_length=30, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    message = models.TextField(blank=True, verbose_name='Сообщение')
    is_processed = models.BooleanField(default=False, verbose_name='Обработана')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f'{self.name} — {self.created_at.strftime("%d.%m.%Y")}'
