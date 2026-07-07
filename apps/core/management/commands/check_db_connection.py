"""
Проверка подключения к базе данных.

Печатает параметры соединения (без пароля) и пытается открыть подключение,
выполнив тестовый запрос. Полезно после заполнения .env реальными данными.

    python manage.py check_db_connection
    python manage.py check_db_connection --database default
"""

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError, Error


class Command(BaseCommand):
    help = 'Проверяет подключение к настроенной базе данных.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--database',
            default='default',
            help='Псевдоним подключения из DATABASES (по умолчанию "default").',
        )

    def handle(self, *args, **options):
        alias = options['database']
        connection = connections[alias]
        cfg = connection.settings_dict

        self.stdout.write(f'Подключение [{alias}]:')
        self.stdout.write(f'  ENGINE : {cfg.get("ENGINE")}')
        self.stdout.write(f'  NAME   : {cfg.get("NAME")}')
        self.stdout.write(f'  HOST   : {cfg.get("HOST") or "(локальный)"}')
        self.stdout.write(f'  PORT   : {cfg.get("PORT") or "(по умолчанию)"}')
        self.stdout.write(f'  USER   : {cfg.get("USER") or "(не задан)"}')
        if cfg.get('OPTIONS'):
            self.stdout.write(f'  OPTIONS: {cfg.get("OPTIONS")}')

        try:
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
        except OperationalError as exc:
            raise self._fail(f'Не удалось подключиться: {exc}')
        except Error as exc:
            raise self._fail(f'Ошибка базы данных: {exc}')

        self.stdout.write(self.style.SUCCESS('✓ Подключение установлено успешно.'))

    def _fail(self, message):
        self.stderr.write(self.style.ERROR(f'✗ {message}'))
        return SystemExit(1)
