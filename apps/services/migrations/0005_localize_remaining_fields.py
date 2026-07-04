from django.db import migrations, models


def copy_service_fields_to_translations(apps, schema_editor):
    Service = apps.get_model('services', 'Service')
    ServiceTranslation = apps.get_model('services', 'ServiceTranslation')
    for service in Service.objects.all():
        ServiceTranslation.objects.filter(
            master_id=service.pk,
            language_code='ru',
        ).update(
            tasks_solved=service.tasks_solved,
            stages=service.stages,
            duration=service.duration,
            client_result=service.client_result,
            meta_title=service.meta_title,
            meta_description=service.meta_description,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_remove_service_full_description_en_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicetranslation',
            name='tasks_solved',
            field=models.TextField(blank=True, help_text='Каждая задача с новой строки', verbose_name='Задачи которые решает'),
        ),
        migrations.AddField(
            model_name='servicetranslation',
            name='stages',
            field=models.JSONField(default=list, help_text='[{"title": "...", "description": "..."}]', verbose_name='Этапы'),
        ),
        migrations.AddField(
            model_name='servicetranslation',
            name='duration',
            field=models.CharField(blank=True, max_length=100, verbose_name='Средняя продолжительность'),
        ),
        migrations.AddField(
            model_name='servicetranslation',
            name='client_result',
            field=models.TextField(blank=True, verbose_name='Что получает заказчик'),
        ),
        migrations.AddField(
            model_name='servicetranslation',
            name='meta_title',
            field=models.CharField(blank=True, max_length=70, verbose_name='Meta Title'),
        ),
        migrations.AddField(
            model_name='servicetranslation',
            name='meta_description',
            field=models.CharField(blank=True, max_length=160, verbose_name='Meta Description'),
        ),
        migrations.RunPython(copy_service_fields_to_translations, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='service',
            name='tasks_solved',
        ),
        migrations.RemoveField(
            model_name='service',
            name='stages',
        ),
        migrations.RemoveField(
            model_name='service',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='service',
            name='client_result',
        ),
        migrations.RemoveField(
            model_name='service',
            name='meta_title',
        ),
        migrations.RemoveField(
            model_name='service',
            name='meta_description',
        ),
    ]
