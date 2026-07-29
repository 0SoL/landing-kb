#!/usr/bin/env sh
set -e

# ── Wait for the database ────────────────────────────────────────────────────
# The database is managed PostgreSQL on Render (external). We poll it briefly so
# the first migrate doesn't race a cold connection. Toggle with WAIT_FOR_DB
# (default "1"; set "0" to skip); tune retries with DB_WAIT_ATTEMPTS.
if [ "${WAIT_FOR_DB:-1}" = "1" ]; then
  echo "Waiting for the database to become available..."
  python <<'PYCODE'
import os
import sys
import time

import django
from django.db import connections
from django.db.utils import OperationalError

django.setup()

max_attempts = int(os.environ.get("DB_WAIT_ATTEMPTS", "30"))
for attempt in range(1, max_attempts + 1):
    try:
        connections["default"].ensure_connection()
        print("Database is available.")
        break
    except OperationalError as exc:
        print(f"[{attempt}/{max_attempts}] Database unavailable, retrying in 2s... ({exc})")
        time.sleep(2)
else:
    print("Database did not become available in time.", file=sys.stderr)
    sys.exit(1)
PYCODE
fi

# ── Django management tasks ──────────────────────────────────────────────────
echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# ── Launch Gunicorn ──────────────────────────────────────────────────────────
# Worker count comes from GUNICORN_WORKERS; when unset, fall back to the
# conventional (2 * CPU cores) + 1. Bind on all interfaces so an external Nginx
# can reverse-proxy to the container.
WORKERS="${GUNICORN_WORKERS:-$(( $(nproc) * 2 + 1 ))}"
echo "Starting Gunicorn with ${WORKERS} worker(s)..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${WORKERS}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
