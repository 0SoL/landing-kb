from .base import *

# SECRET_KEY is REQUIRED in production — no fallback. A missing value raises
# ImproperlyConfigured on boot instead of silently running with a known key.
SECRET_KEY = env('SECRET_KEY')

# DEBUG is read from the DEBUG env var in base settings (defaults to False).
# ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS are required here — a missing
# ALLOWED_HOSTS raises loudly instead of silently serving to any host.
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# DATABASES is built from environment variables in base settings
# (DATABASE_URL or the discrete DB_* variables). These MUST be set in the
# production environment — see DATABASE_SETUP.md.

# TLS is terminated by Nginx; trust its X-Forwarded-Proto so Django knows the
# original request was HTTPS (required for SECURE_SSL_REDIRECT to behave).
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = True
# The container healthcheck hits /health/ directly over plain HTTP (no proxy
# header), so exempt it from the HTTPS redirect to get a clean 200.
SECURE_REDIRECT_EXEMPT = [r'^health/$']

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
