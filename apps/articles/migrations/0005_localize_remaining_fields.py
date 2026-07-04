from django.db import migrations, models


def copy_article_seo_to_translations(apps, schema_editor):
    Article = apps.get_model('articles', 'Article')
    ArticleTranslation = apps.get_model('articles', 'ArticleTranslation')
    for article in Article.objects.all():
        ArticleTranslation.objects.filter(
            master_id=article.pk,
            language_code='ru',
        ).update(
            meta_title=article.meta_title,
            meta_description=article.meta_description,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0004_remove_article_content_en_remove_article_excerpt_en_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='articletranslation',
            name='meta_title',
            field=models.CharField(blank=True, max_length=70, verbose_name='Meta Title'),
        ),
        migrations.AddField(
            model_name='articletranslation',
            name='meta_description',
            field=models.CharField(blank=True, max_length=160, verbose_name='Meta Description'),
        ),
        migrations.RunPython(copy_article_seo_to_translations, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='article',
            name='meta_title',
        ),
        migrations.RemoveField(
            model_name='article',
            name='meta_description',
        ),
    ]
