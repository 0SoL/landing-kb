# syntax=docker/dockerfile:1

FROM python:3.12-slim

# - PYTHONDONTWRITEBYTECODE: don't litter the image with .pyc files.
# - PYTHONUNBUFFERED: stream stdout/stderr straight to the container logs.
# - DJANGO_SETTINGS_MODULE: production settings for every process in the image.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# No apt packages needed: psycopg2-binary and Pillow ship manylinux wheels, so
# there is no build toolchain in the image, and the healthcheck uses Python's
# stdlib (no curl). Keeps the image small and the attack surface minimal.

# Install Python dependencies first so this layer is cached until
# requirements.txt actually changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source.
COPY . .

# Run as an unprivileged user. Pre-create the static output dir and make the
# entrypoint executable before dropping privileges.
RUN adduser --disabled-password --gecos '' appuser \
    && mkdir -p /app/staticfiles \
    && chmod +x /app/entrypoint.sh \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# migrate + collectstatic, then exec Gunicorn (see entrypoint.sh).
ENTRYPOINT ["/app/entrypoint.sh"]
