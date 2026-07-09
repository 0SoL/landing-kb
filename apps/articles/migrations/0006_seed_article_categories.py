from django.db import migrations

# The four article categories are structural: their slugs are hard-coded in
# apps/articles/urls.py and config/urls.py, and article_list() does a
# get_object_or_404 on them — so a database without these rows 404s every
# /novosti/, /investoram/, etc. page. Seeding them here guarantees they exist on
# every environment after `migrate` (the fixtures/initial_data.json path can't:
# ArticleCategory is a parler TranslatableModel, so `name` lives in the
# translation table, and loaddata rejects the fixture). Idempotent — safe to run
# on a DB that already has them.
CATEGORIES = [
    {'slug': 'novosti', 'order': 1, 'ru': 'Новости', 'en': 'News'},
    {'slug': 'investoram', 'order': 2, 'ru': 'Инвесторам', 'en': 'To investors'},
    {'slug': 'tekhnicheskaya-informatsiya', 'order': 3, 'ru': 'Техническая информация', 'en': 'Technical information'},
    {'slug': 'direktoru-kniga', 'order': 4, 'ru': 'Книга директора', 'en': 'Director’s logbook'},
]


def seed_categories(apps, schema_editor):
    ArticleCategory = apps.get_model('articles', 'ArticleCategory')
    ArticleCategoryTranslation = apps.get_model('articles', 'ArticleCategoryTranslation')
    for row in CATEGORIES:
        category, _ = ArticleCategory.objects.get_or_create(
            slug=row['slug'], defaults={'order': row['order']},
        )
        for lang in ('ru', 'en'):
            ArticleCategoryTranslation.objects.get_or_create(
                master=category, language_code=lang, defaults={'name': row[lang]},
            )


def unseed_categories(apps, schema_editor):
    # Reverse is intentionally a no-op: these categories may own real content by
    # the time anyone reverses, and deleting them would cascade to articles.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0005_localize_remaining_fields'),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
