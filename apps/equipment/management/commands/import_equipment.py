"""
Импорт техники из tech.txt в модель Equipment.

Файл tech.txt (в корне проекта) содержит два блока:
  1. Перечень техники — блоки, разделённые пустой строкой. Первая строка блока —
     название, остальные строки — характеристики («Ключ — значение») либо
     описательные признаки (строки без тире).
  2. Текст о преимуществах (начинается со строки «Земляные работы») — при импорте
     техники не используется, обрабатывается отдельно в шаблоне страницы.

Команда идемпотентна: повторный запуск обновляет существующие записи (поиск по
названию), а не создаёт дубликаты.

    python manage.py import_equipment
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.equipment.models import Equipment

# Строка, с которой начинается блок «преимуществ» — граница секции техники.
ADVANTAGES_MARKER = 'Земляные работы'
# Вводная строка перечня, не относящаяся к технике.
INTRO_PREFIX = 'Материально-техническая база'
# Название сводной карточки вспомогательной техники (без индивидуальных характеристик).
AUX_NAME = 'Вспомогательная техника'
# Язык, на котором написан tech.txt (совпадает с PARLER fallback).
SOURCE_LANG = 'ru'
# Разделитель «Ключ — значение» в строках характеристик (длинное тире).
SPEC_SEPARATOR = '—'


class Command(BaseCommand):
    help = 'Импортирует технику из tech.txt в модель Equipment (идемпотентно).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=str(settings.BASE_DIR / 'tech.txt'),
            help='Путь к файлу с данными (по умолчанию tech.txt в корне проекта).',
        )

    def handle(self, *args, **options):
        path = Path(options['file'])
        if not path.exists():
            self.stderr.write(self.style.ERROR(f'Файл не найден: {path}'))
            return

        items = self.parse_equipment(path.read_text(encoding='utf-8'))
        if not items:
            self.stderr.write(self.style.WARNING('В файле не найдено ни одной единицы техники.'))
            return

        created = updated = 0
        with transaction.atomic():
            for order, item in enumerate(items, start=1):
                is_new = self.upsert(item, order * 10)
                verb = 'создано' if is_new else 'обновлено'
                self.stdout.write(f'  [{verb}] {item["name"]} '
                                  f'(характеристик: {len(item["specifications"])})')
                created += is_new
                updated += not is_new

        self.stdout.write(self.style.SUCCESS(
            f'\nГотово. Создано: {created}, обновлено: {updated}, всего в файле: {len(items)}.'
        ))
        self.stdout.write(f'Всего записей Equipment в базе: {Equipment.objects.count()}.')

    # ── Парсинг ──────────────────────────────────────────────────────────────

    def parse_equipment(self, text):
        """Разбирает секцию техники в список словарей с полями модели Equipment."""
        lines = text.splitlines()

        # Отсекаем блок преимуществ.
        cut = len(lines)
        for i, line in enumerate(lines):
            if line.strip() == ADVANTAGES_MARKER:
                cut = i
                break

        # Группируем строки в блоки по пустым строкам.
        blocks, current = [], []
        for line in lines[:cut]:
            if line.strip():
                current.append(line.strip())
            elif current:
                blocks.append(current)
                current = []
        if current:
            blocks.append(current)

        items = []
        for block in blocks:
            # Вводная строка перечня склеена с первым блоком — убираем её.
            if block and block[0].startswith(INTRO_PREFIX):
                block = block[1:]
            if not block:
                continue

            name, rest = block[0], block[1:]

            if name.startswith(AUX_NAME):
                # Вспомогательная техника — сводная карточка без характеристик.
                items.append({
                    'name': name,
                    'purpose': ' '.join(rest).strip() or name,
                    'application': '',
                    'specifications': {},
                })
                continue

            specifications, features = {}, []
            for line in rest:
                if SPEC_SEPARATOR in line:
                    key, _, value = line.partition(SPEC_SEPARATOR)
                    key, value = key.strip(), value.strip()
                    if key and value:
                        specifications[key] = value
                        continue
                features.append(line)

            items.append({
                'name': name,
                'purpose': self.build_purpose(features) or name,
                'application': '',
                'specifications': specifications,
            })

        return items

    @staticmethod
    def build_purpose(features):
        """Собирает описательные признаки в аккуратный текст назначения."""
        sentences = []
        for feature in features:
            feature = feature.strip().rstrip('.')
            if feature:
                sentences.append(feature + '.')
        return ' '.join(sentences)

    # ── Запись ───────────────────────────────────────────────────────────────

    @staticmethod
    def upsert(item, order):
        """Создаёт или обновляет Equipment по названию. Возвращает True, если создано."""
        obj = Equipment.objects.filter(translations__name=item['name']).distinct().first()
        is_new = obj is None
        if is_new:
            obj = Equipment()

        obj.order = order
        obj.is_published = True
        obj.specifications = item['specifications']
        obj.set_current_language(SOURCE_LANG)
        obj.name = item['name']
        obj.purpose = item['purpose']
        obj.application = item['application']
        obj.save()
        return is_new
