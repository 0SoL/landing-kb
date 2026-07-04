from .base import *
import dj_database_url
import os

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    #     "default": dj_database_url.config(
    #     default=os.getenv("DATABASE_URL")
    # )
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
