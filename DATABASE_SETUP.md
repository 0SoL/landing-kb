# Database setup

The database connection is built entirely from environment variables — no
credentials are hard-coded. Configuration lives in `config/settings/base.py`
(`_build_database_config`) and is shared by the `local` and `production`
settings modules.

## Resolution order

The `default` connection is resolved in this order:

1. **`DATABASE_URL`** — a single connection string. If set, it overrides everything.
2. **Discrete `DB_*` variables** — used as soon as `DB_NAME` is set.
3. **SQLite fallback** — `db.sqlite3` in the project root, for zero-config local dev.

## Environment variables

| Variable           | Required            | Default       | Description                                           |
|--------------------|---------------------|---------------|-------------------------------------------------------|
| `DB_ENGINE`        | no                  | `postgresql`  | `postgresql` \| `mysql` \| `sqlite3`                  |
| `DB_NAME`          | yes (external DB)   | —             | Database name. Setting this activates the `DB_*` path.|
| `DB_USER`          | yes                 | empty         | Database user.                                        |
| `DB_PASSWORD`      | yes                 | empty         | Database password.                                    |
| `DB_HOST`          | yes                 | `localhost`   | Host / IP of the external database.                   |
| `DB_PORT`          | no                  | `5432`        | Port (PostgreSQL `5432`, MySQL `3306`).               |
| `DB_CONN_MAX_AGE`  | no                  | `60`          | Persistent connection lifetime in seconds.            |
| `DB_SSL_MODE`      | no (PostgreSQL)     | `require`     | `disable` \| `require` \| `verify-ca` \| `verify-full`|
| `DB_SSL_ROOT_CERT` | only verify-ca/full | empty         | Absolute path to the CA certificate.                  |
| `DATABASE_URL`     | no                  | —             | Alternative single connection string (overrides `DB_*`).|

> SSL note: `DB_SSL_MODE` defaults to `require`, so connections to an external
> PostgreSQL server use SSL unless you explicitly set `DB_SSL_MODE=disable`.

## Steps to connect your database

```bash
# 1. Copy the example env file
cp .env.example .env

# 2. Edit .env — uncomment and fill in the DB_* variables:
#    DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
#    (and DB_SSL_MODE / DB_SSL_ROOT_CERT if your DB needs SSL)

# 3. Install dependencies (PostgreSQL driver psycopg2-binary is already listed)
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 4. Verify the connection (before touching your data)
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py check_db_connection

# 5. Apply migrations
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py migrate
```

For production, use `DJANGO_SETTINGS_MODULE=config.settings.production` and set
the same variables in the server environment. `ALLOWED_HOSTS` is required there.

## Verifying the connection

- `python manage.py check_db_connection` — prints the resolved connection
  parameters (password hidden) and runs a `SELECT 1`.
- `python manage.py migrate --check` — exits non-zero if migrations are missing.
- `python manage.py dbshell` — opens an interactive shell on the configured DB.

## Switching back to local SQLite

Leave the `DB_*` variables (and `DATABASE_URL`) unset/commented in `.env`.
The connection then falls back to `db.sqlite3` automatically.

## Which database driver?

- **PostgreSQL** — `psycopg2-binary` (already in `requirements.txt`).
- **MySQL/MariaDB** — add `mysqlclient` to `requirements.txt` and set `DB_ENGINE=mysql`.

## Docker

This project does not ship a `docker-compose.yml`. When connecting to an
external database there is no local DB container to disable — the app talks to
your external host directly via the variables above.
