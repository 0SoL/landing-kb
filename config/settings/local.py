from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# DATABASES is built from environment variables in base settings.
# With no DB_* / DATABASE_URL vars set in .env, it falls back to local SQLite.

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
