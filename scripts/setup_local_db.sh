#!/usr/bin/env bash
# Creates the local Postgres role + database used by backend/.env.example.
# Must be run as (or via) a Postgres superuser:
#   Debian/Ubuntu: sudo -u postgres ./scripts/setup_local_db.sh
#   macOS (Homebrew postgres): ./scripts/setup_local_db.sh
set -euo pipefail

DB_NAME="${POSTGRES_DB:-pricewatch}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_PASSWORD="${POSTGRES_PASSWORD:-postgres}"

if [ "$(psql -tAc "SELECT 1 FROM pg_roles WHERE rolname = '${DB_USER}'")" != "1" ]; then
    psql -c "CREATE ROLE \"${DB_USER}\" LOGIN PASSWORD '${DB_PASSWORD}';"
fi

if [ "$(psql -tAc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'")" != "1" ]; then
    createdb -O "${DB_USER}" "${DB_NAME}"
fi

echo "Database '${DB_NAME}' ready (owner: ${DB_USER})."
