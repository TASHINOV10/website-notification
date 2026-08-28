"""
Creates the Postgres database from DATABASE_URL (backend/.env) if it doesn't
already exist yet. Cross-platform (Windows/macOS/Linux) -- run from inside
backend/, after installing requirements.txt (psycopg2 is already a backend
dependency, this needs nothing extra):

    python scripts/setup_local_db.py

This only creates the *database*. It assumes the role/password in
DATABASE_URL already exists on your Postgres server (true for both the
default Windows installer and Homebrew/apt installs) -- it does not create
roles.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg2
from sqlalchemy.engine import make_url

from app.config import settings


def main():
    url = make_url(settings.database_url)
    db_name = url.database

    conn = psycopg2.connect(
        host=url.host or "localhost",
        port=url.port or 5432,
        user=url.username,
        password=url.password,
        dbname="postgres",
    )
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if cur.fetchone() is None:
                cur.execute(f'CREATE DATABASE "{db_name}"')
                print(f"Created database {db_name!r}.")
            else:
                print(f"Database {db_name!r} already exists.")
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except psycopg2.OperationalError as exc:
        print(f"Could not connect to Postgres: {exc}", file=sys.stderr)
        print(
            "Check that Postgres is running and that DATABASE_URL in backend/.env "
            "matches a role/password that already exists on your server.",
            file=sys.stderr,
        )
        sys.exit(1)
