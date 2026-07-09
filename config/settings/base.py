from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env', overwrite=True)

print(BASE_DIR / '.env')  # добавьте временно и проверьте вывод

print("DB_HOST:", env("DB_HOST", default="NOT FOUND"))

print("DB_NAME:", env("DB_NAME", default="NOT FOUND"))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-dev-key-change-in-production')
DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

DJANGO_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'storages',
]

LOCAL_APPS = [
    'apps.core',
    'apps.projects',
    'apps.services',
    'apps.equipment',
    'apps.articles',
    'apps.seo',
]

INSTALLED_APPS = DJANGO_APPS + ['parler'] + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': False,
        'OPTIONS': {
            'environment': 'config.jinja2.environment',
            'match_extension': '.html',
            'match_regex': r'^(?!admin/).*',
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
            'undefined': 'jinja2.Undefined',
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ── Database ────────────────────────────────────────────────────────────────
# The connection is assembled from environment variables so that no credentials
# are ever hard-coded. Resolution order:
#   1. DATABASE_URL      — a single connection string (overrides everything else).
#   2. Discrete DB_* vars — DB_ENGINE / DB_NAME / DB_USER / DB_PASSWORD / ...
#   3. SQLite fallback    — zero-config local development only.
# See DATABASE_SETUP.md for the full list of variables.
_DB_ENGINE_ALIASES = {
    'postgres': 'django.db.backends.postgresql',
    'postgresql': 'django.db.backends.postgresql',
    'mysql': 'django.db.backends.mysql',
    'mariadb': 'django.db.backends.mysql',
    'sqlite': 'django.db.backends.sqlite3',
    'sqlite3': 'django.db.backends.sqlite3',
}


def _build_database_config():
    # 1. Single connection string wins if provided.
    if env('DATABASE_URL', default=''):
        print("Using DATABASE_URL")
        return env.db('DATABASE_URL')

    # 2. Discrete variables — activated as soon as a database name is given.
    if env('DB_NAME', default=''):
        print(f"Using discrete vars: DB_NAME={env('DB_NAME')}, DB_HOST={env('DB_HOST', default='localhost')}")
        engine = env('DB_ENGINE', default='postgresql')
        engine = _DB_ENGINE_ALIASES.get(engine.lower(), engine)

        options = {}
        if 'postgresql' in engine:
            sslmode = env('DB_SSL_MODE', default='require')
            if sslmode:
                options['sslmode'] = sslmode
            ssl_root_cert = env('DB_SSL_ROOT_CERT', default='')
            if ssl_root_cert:
                options['sslrootcert'] = ssl_root_cert

        config = {
            'ENGINE': engine,
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER', default=''),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
            'CONN_MAX_AGE': env.int('DB_CONN_MAX_AGE', default=60),
        }
        if options:
            config['OPTIONS'] = options
        return config

    # 3. Local development fallback.
    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }


DATABASES = {'default': _build_database_config()}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

PARLER_LANGUAGES = {
    None: (
        {'code': 'ru'},
        {'code': 'en'},
    ),
    'default': {
        'fallback': 'ru',
        'hide_untranslated': False,
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@example.com')
INQUIRY_RECIPIENT_EMAIL = env('INQUIRY_RECIPIENT_EMAIL', default='info@example.com')

UNFOLD = {
    'SITE_TITLE': 'РЖД-Инфра Казахстан',
    'SITE_HEADER': 'Управление сайтом',
    'SITE_URL': '/',
    'COLORS': {
        'primary': {
            '50': '255 248 235',
            '100': '255 237 213',
            '200': '255 215 163',
            '300': '253 186 116',
            '400': '252 161 78',
            '500': '200 146 42',
            '600': '180 110 20',
            '700': '155 85 15',
            '800': '120 53 15',
            '900': '92 40 12',
            '950': '60 25 8',
        },
    },
}
