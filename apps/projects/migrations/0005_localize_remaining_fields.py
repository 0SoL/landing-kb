from django.db import migrations, models


def copy_project_fields_to_translations(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    ProjectTranslation = apps.get_model('projects', 'ProjectTranslation')
    for project in Project.objects.all():
        ProjectTranslation.objects.filter(
            master_id=project.pk,
            language_code='ru',
        ).update(
            location=project.location,
            budget_display=project.budget_display,
            meta_title=project.meta_title,
            meta_description=project.meta_description,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_remove_project_result_en_remove_project_solution_en_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='projecttranslation',
            name='location',
            field=models.CharField(blank=True, max_length=200, verbose_name='Локация'),
        ),
        migrations.AddField(
            model_name='projecttranslation',
            name='budget_display',
            field=models.CharField(blank=True, help_text='Например: от 150 млн тг', max_length=100, verbose_name='Бюджет (отображение)'),
        ),
        migrations.AddField(
            model_name='projecttranslation',
            name='meta_title',
            field=models.CharField(blank=True, max_length=70, verbose_name='Meta Title'),
        ),
        migrations.AddField(
            model_name='projecttranslation',
            name='meta_description',
            field=models.CharField(blank=True, max_length=160, verbose_name='Meta Description'),
        ),
        migrations.RunPython(copy_project_fields_to_translations, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='project',
            name='location',
        ),
        migrations.RemoveField(
            model_name='project',
            name='budget_display',
        ),
        migrations.RemoveField(
            model_name='project',
            name='meta_title',
        ),
        migrations.RemoveField(
            model_name='project',
            name='meta_description',
        ),
    ]
