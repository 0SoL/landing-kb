"""
Импорт проектов (кейсов) из projects.txt в модель Project.

Файл projects.txt (в корне проекта) — свободный текст. Каждый проект описан
блоком: строка-заголовок, дата, секция «Задачи…:» (маркированный список задач)
и секция «Особые факты…:» (факты: заказчик, тип объекта, расположение, сроки).
Между проектами встречаются служебные секции («Период активного развития…»,
«НАШИ ЗАКАЗЧИКИ:») — при импорте они пропускаются.

Команда идемпотентна: повторный запуск обновляет проекты по названию, а не
создаёт дубликаты.

    python manage.py import_projects
"""

import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.projects.models import Project

SOURCE_LANG = 'ru'

# Маркеры секций внутри блока проекта.
TASK_MARKER = 'Задачи'
FACTS_MARKER = 'Особые факты'
# Служебные секции — границы, не относящиеся к проектам.
STOP_HEADERS = ('Период активного развития', 'НАШИ ЗАКАЗЧИКИ')

# Диапазон дат вида «2013 – 2015» / «2020-2023».
DATE_RANGE_RE = re.compile(r'(\d{4})\s*[–—-]\s*(\d{4})')
DATE_ONLY_LINE_RE = re.compile(r'^\s*\d{4}\s*[–—-]\s*\d{4}\s*$')

# Извлечение полей из «Особых фактов» / заголовка.
CLIENT_RE = re.compile(r'^Заказчик[и]?\s*:\s*(.+)$', re.IGNORECASE)
LOCATION_RE = re.compile(r'^(?:Расположение|Место расположения)\s*:\s*(.+)$', re.IGNORECASE)
# Запасной вариант, когда явной строки «Расположение:» нет («…расположен на станции Достык»).
LOCATION_FALLBACK_RE = re.compile(r'располож\w*\s+(?:на|в)\s+(.+?)[;.,]', re.IGNORECASE)
TYPE_RE = re.compile(r'^Тип\s+(?:объекта|проекта)\s*:\s*(.+)$', re.IGNORECASE)
DEADLINE_RE = re.compile(r'Сроки реализации\s*:\s*\d{4}\s*[–—-]\s*(\d{4})', re.IGNORECASE)
CLIENT_FROM_TITLE_RE = re.compile(r'\bдля\s+(.+)$', re.IGNORECASE)

# Сопоставление типа объекта с CLIENT_TYPES. Порядок = приоритет.
# Ключи ищутся по границе слова, чтобы «экспортный», «спорт» и т.п. не давали
# ложных срабатываний на «порт».
CLIENT_TYPE_KEYWORDS = [
    ('port', re.compile(r'\bпорт', re.IGNORECASE)),
    ('terminal', re.compile(r'\bтерминал', re.IGNORECASE)),
    ('logistics', re.compile(r'\bлогист', re.IGNORECASE)),
    ('factory', re.compile(r'\bзавод', re.IGNORECASE)),
]
# Ручные переопределения типа по фрагменту названия (когда «Тип объекта» в файле
# не отражает суть объекта). «Саржа» — первый частный морской порт РК.
CLIENT_TYPE_OVERRIDES = {'Саржа': 'port'}

# Транслитерация для генерации slug в стиле уже существующих проектов.
TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}

SOLUTION_PLACEHOLDER = (
    'Проект реализован собственными силами компании — от проектирования до '
    'строительства и ввода в эксплуатацию, без привлечения субподрядных организаций.'
)


class Command(BaseCommand):
    help = 'Импортирует проекты из projects.txt в модель Project (идемпотентно).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=str(settings.BASE_DIR / 'projects.txt'),
            help='Путь к файлу с данными (по умолчанию projects.txt в корне проекта).',
        )

    def handle(self, *args, **options):
        path = Path(options['file'])
        if not path.exists():
            self.stderr.write(self.style.ERROR(f'Файл не найден: {path}'))
            return

        projects = self.parse_projects(path.read_text(encoding='utf-8'))
        if not projects:
            self.stderr.write(self.style.WARNING('В файле не найдено ни одного проекта.'))
            return

        created = updated = 0
        used_slugs = set(Project.objects.values_list('slug', flat=True))
        with transaction.atomic():
            for order, item in enumerate(projects, start=1):
                is_new = self.upsert(item, order, used_slugs)
                verb = 'создан' if is_new else 'обновлён'
                flag = f'  ⚠ {item["type_note"]}' if item['type_note'] else ''
                self.stdout.write(
                    f'  [{verb}] {item["title"][:60]}… '
                    f'→ тип: {item["client_type"]}, год: {item["year"]}{flag}'
                )
                created += is_new
                updated += not is_new

        self.stdout.write(self.style.SUCCESS(
            f'\nГотово. Создано: {created}, обновлено: {updated}, всего в файле: {len(projects)}.'
        ))
        self.stdout.write(f'Всего записей Project в базе: {Project.objects.count()}.')
        self.stdout.write(self.style.WARNING(
            'Поле «Наше решение» заполнено черновым текстом-заглушкой — отредактируйте в админке.'
        ))

    # ── Парсинг ──────────────────────────────────────────────────────────────

    def parse_projects(self, text):
        lines = text.splitlines()

        task_markers = [i for i, l in enumerate(lines) if l.strip().startswith(TASK_MARKER)]
        facts_markers = [i for i, l in enumerate(lines) if l.strip().startswith(FACTS_MARKER)]

        # Индексы строк-заголовков всех проектов (нужны как границы для «результата»).
        title_indices = [self._find_title_index(lines, tm) for tm in task_markers]

        # Границы служебных секций.
        stop_indices = set(title_indices)
        for i, l in enumerate(lines):
            if l.strip().startswith(STOP_HEADERS):
                stop_indices.add(i)

        projects = []
        for k, task_marker in enumerate(task_markers):
            facts_marker = next((f for f in facts_markers if f > task_marker), len(lines))
            title_idx = title_indices[k]

            title = lines[title_idx].strip()
            task_lines = self._collect(lines, task_marker + 1, facts_marker)
            result_stop = min((s for s in stop_indices if s > facts_marker), default=len(lines))
            fact_lines = self._collect(lines, facts_marker + 1, result_stop)

            corpus_for_year = [title, lines[task_marker]] + self._between_dates(lines, title_idx, task_marker)
            projects.append(self._build_item(title, task_lines, fact_lines, corpus_for_year))

        return projects

    @staticmethod
    def _find_title_index(lines, task_marker):
        """Заголовок проекта — первая непустая строка перед «Задачи…», не являющаяся датой."""
        i = task_marker - 1
        while i >= 0:
            stripped = lines[i].strip()
            if stripped and not DATE_ONLY_LINE_RE.match(stripped):
                return i
            i -= 1
        return task_marker  # fallback (не должно происходить)

    @staticmethod
    def _between_dates(lines, title_idx, task_marker):
        """Строки между заголовком и «Задачи…» (обычно строка с датой)."""
        return [lines[i].strip() for i in range(title_idx + 1, task_marker) if lines[i].strip()]

    @staticmethod
    def _collect(lines, start, end):
        return [lines[i].strip() for i in range(start, min(end, len(lines))) if lines[i].strip()]

    def _build_item(self, title, task_lines, fact_lines, corpus_for_year):
        task = self._join(task_lines)
        result = self._join(fact_lines)

        client = self._first_match(fact_lines, CLIENT_RE)
        if not client:
            m = CLIENT_FROM_TITLE_RE.search(title)
            client = m.group(1).strip() if m else ''
        location = self._first_match(fact_lines, LOCATION_RE)
        if not location:
            for line in fact_lines:
                m = LOCATION_FALLBACK_RE.search(line)
                if m:
                    location = m.group(1).strip()
                    break
        type_text = self._first_match(fact_lines, TYPE_RE)

        client_type, type_note = self.map_client_type(type_text, title)
        year = self._extract_year(fact_lines, corpus_for_year)

        return {
            'title': title,
            'task': task,
            'solution': SOLUTION_PLACEHOLDER,
            'result': result,
            'client': client.rstrip(' ;.'),
            'location': location.rstrip(' ;.'),
            'client_type': client_type,
            'type_note': type_note,
            'year': year,
        }

    @staticmethod
    def _join(lines):
        return ' '.join(l.lstrip('-–— ').strip() for l in lines).strip()

    @staticmethod
    def _first_match(lines, regex):
        for line in lines:
            m = regex.match(line)
            if m:
                return m.group(1).strip()
        return ''

    def map_client_type(self, type_text, title):
        """Возвращает (client_type, note). note != '' — если требуется внимание."""
        for fragment, ct in CLIENT_TYPE_OVERRIDES.items():
            if fragment in title:
                return ct, f'тип задан вручную ({ct}) для «{fragment}»'

        source = type_text or title
        for ct, pattern in CLIENT_TYPE_KEYWORDS:
            if pattern.search(source):
                note = '' if type_text else 'тип выведен из названия (нет строки «Тип объекта»)'
                return ct, note
        return 'other', f'тип не распознан → other (исходный текст: «{source[:60]}»)'

    @staticmethod
    def _extract_year(fact_lines, corpus_for_year):
        for line in fact_lines:
            m = DEADLINE_RE.search(line)
            if m:
                return int(m.group(1))
        for line in corpus_for_year:
            m = DATE_RANGE_RE.search(line)
            if m:
                return int(m.group(2))
        for line in corpus_for_year:
            m = re.search(r'(\d{4})', line)
            if m:
                return int(m.group(1))
        return 0

    # ── Запись ───────────────────────────────────────────────────────────────

    def upsert(self, item, order, used_slugs):
        obj = Project.objects.filter(translations__title=item['title']).distinct().first()
        is_new = obj is None
        if is_new:
            obj = Project(slug=self._unique_slug(item['title'], used_slugs))
            used_slugs.add(obj.slug)

        obj.client = item['client']
        obj.client_type = item['client_type']
        obj.year = item['year']
        obj.order = order
        obj.is_published = True
        obj.set_current_language(SOURCE_LANG)
        obj.title = item['title']
        obj.task = item['task']
        obj.solution = item['solution']
        obj.result = item['result']
        obj.location = item['location']
        obj.save()
        return is_new

    def _unique_slug(self, title, used_slugs):
        base = slugify(self._transliterate(title))[:50].rstrip('-') or 'proekt'
        slug = base
        n = 2
        while slug in used_slugs:
            slug = f'{base[:47]}-{n}'
            n += 1
        return slug

    @staticmethod
    def _transliterate(text):
        return ''.join(TRANSLIT.get(ch, TRANSLIT.get(ch.lower(), ch)) if ch.lower() in TRANSLIT else ch
                       for ch in text)
