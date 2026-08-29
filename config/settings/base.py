from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
# Reads a local .env file when present (dev). In containers no .env is copied
# into the image, so values come straight from the process environment
# (docker-compose `env_file`) — read_env is a no-op then.
environ.Env.read_env(BASE_DIR / '.env', overwrite=True)

SECRET_KEY = env('SECRET_KEY', default='django-insecure-dev-key-change-in-production')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

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
        return env.db('DATABASE_URL')

    # 2. Discrete variables — activated as soon as a database name is given.
    if env('DB_NAME', default=''):
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

# ── Storage backends (Django 4.2+ STORAGES dict) ─────────────────────────────
# Static files are always served by WhiteNoise. Media (user uploads) is served
# from S3-compatible object storage (AWS S3 / Cloudflare R2 / Backblaze B2)
# because Render.com's filesystem is ephemeral — uploads would vanish on every
# redeploy/restart. When no bucket is configured (e.g. local dev), media falls
# back to the local filesystem so development works with zero cloud setup.
#
# All credentials come from environment variables — never hard-code them.
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')
# Endpoint URL is required for R2 / Backblaze; leave unset for pure AWS S3.
AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL', default='') or None
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='') or None
# Optional CDN / custom domain that serves the bucket (e.g. cdn.example.com).
AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN', default='') or None
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False  # objects are public — serve plain, unsigned URLs

_STATICFILES_BACKEND = {
    'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
}

if AWS_STORAGE_BUCKET_NAME:
    STORAGES = {
        'default': {'BACKEND': 'storages.backends.s3.S3Storage'},
        'staticfiles': _STATICFILES_BACKEND,
    }
    # Derive MEDIA_URL from the way the bucket is exposed.
    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
    elif AWS_S3_ENDPOINT_URL:
        MEDIA_URL = f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/"
    else:
        _region = f'.{AWS_S3_REGION_NAME}' if AWS_S3_REGION_NAME else ''
        MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3{_region}.amazonaws.com/'
else:
    # Local development fallback — filesystem media.
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': _STATICFILES_BACKEND,
    }
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Logging ──────────────────────────────────────────────────────────────────
# Everything goes to the console (stdout/stderr) so `docker logs` is the single
# source of truth — no log files inside the container. Level is env-tunable.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': env('DJANGO_LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@example.com')
INQUIRY_RECIPIENT_EMAIL = env('INQUIRY_RECIPIENT_EMAIL', default='info@example.com')

# ── Social networks ─────────────────────────────────────────────────────────
# Only Instagram and YouTube are published. A blank value hides that link
# everywhere (contacts page, footer, and the Organization `sameAs` list).
SOCIAL_INSTAGRAM_URL = env('SOCIAL_INSTAGRAM_URL', default='https://www.instagram.com/konkurent_b/')
# YouTube is intentionally hidden for now. The rendering code is fully intact —
# set SOCIAL_YOUTUBE_URL to the channel URL to bring the link back everywhere.
SOCIAL_YOUTUBE_URL = env('SOCIAL_YOUTUBE_URL', default='')

UNFOLD = {
    'SITE_TITLE': 'Конкурент-Б',
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
