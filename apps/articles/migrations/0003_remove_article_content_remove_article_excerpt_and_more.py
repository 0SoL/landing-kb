import django.db.models.deletion
import parler.models
from django.db import migrations, models


def copy_article_translations(apps, schema_editor):
    ArticleCategory = apps.get_model('articles', 'ArticleCategory')
    ArticleCategoryTranslation = apps.get_model('articles', 'ArticleCategoryTranslation')
    Article = apps.get_model('articles', 'Article')
    ArticleTranslation = apps.get_model('articles', 'ArticleTranslation')

    for cat in ArticleCategory.objects.all():
        ArticleCategoryTranslation.objects.get_or_create(
            master_id=cat.pk,
            language_code='ru',
            defaults={'name': cat.name},
        )
        if cat.name_en:
            ArticleCategoryTranslation.objects.get_or_create(
                master_id=cat.pk,
                language_code='en',
                defaults={'name': cat.name_en},
            )

    for article in Article.objects.all():
        ArticleTranslation.objects.get_or_create(
            master_id=article.pk,
            language_code='ru',
            defaults={
                'title': article.title,
                'excerpt': article.excerpt,
                'content': article.content,
            },
        )
        if article.title_en:
            ArticleTranslation.objects.get_or_create(
                master_id=article.pk,
                language_code='en',
                defaults={
                    'title': article.title_en,
                    'excerpt': article.excerpt_en,
                    'content': article.content_en,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_article_content_en_article_excerpt_en_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleCategoryTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='articles.articlecategory')),
            ],
            options={
                'verbose_name': 'Категория статей Translation',
                'db_table': 'articles_articlecategory_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArticleTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=250, verbose_name='Заголовок')),
                ('excerpt', models.TextField(max_length=350, verbose_name='Анонс')),
                ('content', models.TextField(verbose_name='Содержание (HTML)')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='articles.article')),
            ],
            options={
                'verbose_name': 'Статья Translation',
                'db_table': 'articles_article_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(copy_article_translations, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='article',
            name='content_en',
            field=models.TextField(blank=True, verbose_name='Содержание (HTML) (EN) [legacy]'),
        ),
        migrations.AlterField(
            model_name='article',
            name='excerpt_en',
            field=models.TextField(blank=True, max_length=350, verbose_name='Анонс (EN) [legacy]'),
        ),
        migrations.AlterField(
            model_name='article',
            name='title_en',
            field=models.CharField(blank=True, max_length=250, verbose_name='Заголовок (EN) [legacy]'),
        ),
        migrations.AlterField(
            model_name='articlecategory',
            name='name_en',
            field=models.CharField(blank=True, max_length=100, verbose_name='Название (EN) [legacy]'),
        ),
        migrations.RemoveField(
            model_name='article',
            name='content',
        ),
        migrations.RemoveField(
            model_name='article',
            name='excerpt',
        ),
        migrations.RemoveField(
            model_name='article',
            name='title',
        ),
        migrations.RemoveField(
            model_name='articlecategory',
            name='name',
        ),
    ]
