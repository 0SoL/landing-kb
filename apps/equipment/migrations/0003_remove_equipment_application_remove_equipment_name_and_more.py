import django.db.models.deletion
import parler.models
from django.db import migrations, models


def copy_equipment_translations(apps, schema_editor):
    EquipmentCategory = apps.get_model('equipment', 'EquipmentCategory')
    EquipmentCategoryTranslation = apps.get_model('equipment', 'EquipmentCategoryTranslation')
    Equipment = apps.get_model('equipment', 'Equipment')
    EquipmentTranslation = apps.get_model('equipment', 'EquipmentTranslation')

    for cat in EquipmentCategory.objects.all():
        EquipmentCategoryTranslation.objects.get_or_create(
            master_id=cat.pk,
            language_code='ru',
            defaults={'name': cat.name},
        )
        if cat.name_en:
            EquipmentCategoryTranslation.objects.get_or_create(
                master_id=cat.pk,
                language_code='en',
                defaults={'name': cat.name_en},
            )

    for item in Equipment.objects.all():
        EquipmentTranslation.objects.get_or_create(
            master_id=item.pk,
            language_code='ru',
            defaults={
                'name': item.name,
                'purpose': item.purpose,
                'application': item.application,
            },
        )
        if item.name_en:
            EquipmentTranslation.objects.get_or_create(
                master_id=item.pk,
                language_code='en',
                defaults={
                    'name': item.name_en,
                    'purpose': item.purpose_en,
                    'application': item.application_en,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0002_equipment_application_en_equipment_name_en_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentCategoryTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='equipment.equipmentcategory')),
            ],
            options={
                'verbose_name': 'Категория техники Translation',
                'db_table': 'equipment_equipmentcategory_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EquipmentTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('purpose', models.TextField(verbose_name='Назначение')),
                ('application', models.TextField(blank=True, verbose_name='Где применяется')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='equipment.equipment')),
            ],
            options={
                'verbose_name': 'Техника Translation',
                'db_table': 'equipment_equipment_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(copy_equipment_translations, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='equipment',
            name='application_en',
            field=models.TextField(blank=True, verbose_name='Где применяется (EN) [legacy]'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='name_en',
            field=models.CharField(blank=True, max_length=200, verbose_name='Название (EN) [legacy]'),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='purpose_en',
            field=models.TextField(blank=True, verbose_name='Назначение (EN) [legacy]'),
        ),
        migrations.AlterField(
            model_name='equipmentcategory',
            name='name_en',
            field=models.CharField(blank=True, max_length=100, verbose_name='Название (EN) [legacy]'),
        ),
        migrations.RemoveField(
            model_name='equipment',
            name='application',
        ),
        migrations.RemoveField(
            model_name='equipment',
            name='name',
        ),
        migrations.RemoveField(
            model_name='equipment',
            name='purpose',
        ),
        migrations.RemoveField(
            model_name='equipmentcategory',
            name='name',
        ),
    ]
