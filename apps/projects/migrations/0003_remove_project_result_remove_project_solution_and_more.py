import django.db.models.deletion
import parler.models
from django.db import migrations, models


def copy_project_translations(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    ProjectTranslation = apps.get_model('projects', 'ProjectTranslation')
    for project in Project.objects.all():
        ProjectTranslation.objects.get_or_create(
            master_id=project.pk,
            language_code='ru',
            defaults={
                'title': project.title,
                'task': project.task,
                'solution': project.solution,
                'result': project.result,
            },
        )
        if project.title_en:
            ProjectTranslation.objects.get_or_create(
                master_id=project.pk,
                language_code='en',
                defaults={
                    'title': project.title_en,
                    'task': project.task_en,
                    'solution': project.solution_en,
                    'result': project.result_en,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_project_result_en_project_solution_en_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('task', models.TextField(verbose_name='Задача клиента')),
                ('solution', models.TextField(verbose_name='Наше решение')),
                ('result', models.TextField(verbose_name='Результат')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='projects.project')),
            ],
            options={
                'verbose_name': 'Проект Translation',
                'db_table': 'projects_project_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(copy_project_translations, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='project',
            name='result_en',
            field=models.TextField(blank=True, verbose_name='Результат (EN) [legacy]'),
        ),
        migrations.AlterField(
            model_name='project',
            name='solution_en',
            field=models.TextField(blank=True, verbose_name='Наше решение (EN) [legacy]'),
        ),
        migrations.AlterField(
            model_name='project',
            name='task_en',
            field=models.TextField(blank=True, verbose_name='Задача клиента (EN) [legacy]'),
        ),
        migrations.AlterField(
            model_name='project',
            name='title_en',
            field=models.CharField(blank=True, max_length=200, verbose_name='Название (EN) [legacy]'),
        ),
        migrations.RemoveField(
            model_name='project',
            name='result',
        ),
        migrations.RemoveField(
            model_name='project',
            name='solution',
        ),
        migrations.RemoveField(
            model_name='project',
            name='task',
        ),
        migrations.RemoveField(
            model_name='project',
            name='title',
        ),
    ]
