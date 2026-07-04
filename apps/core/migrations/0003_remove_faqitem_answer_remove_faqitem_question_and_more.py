import django.db.models.deletion
import parler.models
from django.db import migrations, models


def copy_faq_translations(apps, schema_editor):
    FAQItem = apps.get_model('core', 'FAQItem')
    FAQItemTranslation = apps.get_model('core', 'FAQItemTranslation')
    for item in FAQItem.objects.all():
        FAQItemTranslation.objects.get_or_create(
            master_id=item.pk,
            language_code='ru',
            defaults={'question': item.question, 'answer': item.answer},
        )
        if item.question_en:
            FAQItemTranslation.objects.get_or_create(
                master_id=item.pk,
                language_code='en',
                defaults={'question': item.question_en, 'answer': item.answer_en},
            )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_faqitem_answer_en_faqitem_question_en'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQItemTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('question', models.CharField(max_length=500, verbose_name='Вопрос')),
                ('answer', models.TextField(verbose_name='Ответ')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='core.faqitem')),
            ],
            options={
                'verbose_name': 'FAQ вопрос Translation',
                'db_table': 'core_faqitem_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(copy_faq_translations, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='faqitem',
            name='answer_en',
            field=models.TextField(blank=True, verbose_name='Ответ (EN) [legacy]'),
        ),
        migrations.AlterField(
            model_name='faqitem',
            name='question_en',
            field=models.CharField(blank=True, max_length=500, verbose_name='Вопрос (EN) [legacy]'),
        ),
        migrations.RemoveField(
            model_name='faqitem',
            name='answer',
        ),
        migrations.RemoveField(
            model_name='faqitem',
            name='question',
        ),
    ]
