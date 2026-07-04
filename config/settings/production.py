from .base import *
import environ
import dj_database_url
import os

env = environ.Env()

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DATABASES = {
    'default': env.db('DATABASE_URL')
}

# DATABASES = {
#     "default": dj_database_url.config(
#         default=os.getenv("DATABASE_URL")
#     )
# }

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
