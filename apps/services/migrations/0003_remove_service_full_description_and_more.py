import django.db.models.deletion
import parler.models
from django.db import migrations, models


def copy_service_translations(apps, schema_editor):
    ServiceCategory = apps.get_model('services', 'ServiceCategory')
    ServiceCategoryTranslation = apps.get_model('services', 'ServiceCategoryTranslation')
    Service = apps.get_model('services', 'Service')
    ServiceTranslation = apps.get_model('services', 'ServiceTranslation')

    for cat in ServiceCategory.objects.all():
        ServiceCategoryTranslation.objects.get_or_create(
            master_id=cat.pk,
            language_code='ru',
            defaults={'name': cat.name},
        )
        if cat.name_en:
            ServiceCategoryTranslation.objects.get_or_create(
                master_id=cat.pk,
                language_code='en',
                defaults={'name': cat.name_en},
            )

    for svc in Service.objects.all():
        ServiceTranslation.objects.get_or_create(
            master_id=svc.pk,
            language_code='ru',
            defaults={
                'title': svc.title,
                'short_description': svc.short_description,
                'full_description': svc.full_description,
            },
        )
        if svc.title_en:
            ServiceTranslation.objects.get_or_create(
                master_id=svc.pk,
                language_code='en',
                defaults={
                    'title': svc.title_en,
                    'short_description': svc.short_description_en,
                    'full_description': svc.full_description_en,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_service_full_description_en_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceCategoryTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='services.servicecategory')),
            ],
            options={
                'verbose_name': 'Категория услуг Translation',
                'db_table': 'services_servicecategory_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('short_description', models.TextField(max_length=300, verbose_name='Краткое описание')),
                ('full_description', models.TextField(verbose_name='Полное описание')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='services.service')),
            ],
            options={
                'verbose_name': 'Услуга Translation',
                'db_table': 'services_service_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(copy_service_translations, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='service',
            name='full_description_en',
            field=models.TextField(blank=True, verbose_name='Полное описание (EN) [legacy]'),
        ),
        migrations.AlterField(
            model_name='service',
            name='short_description_en',
            field=models.TextField(blank=True, max_length=300, verbose_name='Краткое описание (EN) [legacy]'),
        ),
        migrations.AlterField(
            model_name='service',
            name='title_en',
            field=models.CharField(blank=True, max_length=200, verbose_name='Название (EN) [legacy]'),
        ),
        migrations.AlterField(
            model_name='servicecategory',
            name='name_en',
            field=models.CharField(blank=True, max_length=100, verbose_name='Название (EN) [legacy]'),
        ),
        migrations.RemoveField(
            model_name='service',
            name='full_description',
        ),
        migrations.RemoveField(
            model_name='service',
            name='short_description',
        ),
        migrations.RemoveField(
            model_name='service',
            name='title',
        ),
        migrations.RemoveField(
            model_name='servicecategory',
            name='name',
        ),
    ]
