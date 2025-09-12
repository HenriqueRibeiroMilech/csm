#!/usr/bin/env sh
set -e

poetry run alembic upgrade head

PORT_ENV=${PORT:-8000}
exec poetry run uvicorn --host 0.0.0.0 --port "$PORT_ENV" backend.app:app
