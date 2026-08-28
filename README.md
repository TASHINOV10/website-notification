# PriceWatch

Track a product listing URL, get notified by email when the price changes. A minimal,
self-hostable take on [changedetection.io](https://changedetection.io/), scoped to price
tracking.

## Stack

- **Frontend**: React (Vite), a landing page plus a small dashboard app, served in
  production by a tiny Express static server
- **Backend**: FastAPI (REST API, scraping, scheduling, email notifications)
- **DB**: PostgreSQL
- **Scheduler**: APScheduler running inside the FastAPI process (polls every
  `SCHEDULER_TICK_SECONDS`, checks whichever watches are due based on their own
  `check_interval_minutes`)

## How it works

1. You add a watch: a URL, an optional CSS selector pointing at the price element, an
   email to notify, and a check interval.
2. The backend periodically fetches the page, extracts the price (via the selector if
   given, otherwise by trying a few common price patterns — `itemprop=price`,
   `og:price:amount`, `.price`, etc. — and falling back to a regex scan of the page text).
3. Each check is recorded in `price_history`. If the price differs from the last known
   price, an email is sent.

## Project layout

```
backend/            FastAPI app
  app/
    main.py          app factory, startup (creates tables, starts scheduler)
    config.py         env-based settings
    database.py        SQLAlchemy engine/session
    models.py           Watch, PriceHistory
    schemas.py           Pydantic request/response models
    scraper.py            fetch + extract price from HTML
    notifier.py            SMTP email sending
    scheduler.py             periodic job that checks due watches
    routers/watches.py        CRUD + manual "check now" endpoint
frontend/           React (Vite) SPA, talks to the backend over HTTP
  src/
    App.jsx           routes: "/" landing, "/app" dashboard, "/app/new", "/app/watches/:id"
    pages/             Landing, Dashboard, NewWatch, WatchDetail
    api.js              fetch wrapper, reads the API base from runtime config
  server.js           production static file server; also serves /config.js so the
                       backend URL can be set per-deployment without rebuilding
docker-compose.yml   postgres + backend + frontend, for local dev
```

## Local development (no Docker)

Requirements: Python 3.11+, Node 18+, a Postgres server already running locally (the
official Windows installer, Postgres.app/Homebrew on macOS, or `apt install postgresql`
on Linux all work — whatever admin user/password you set up during that install is what
goes in `DATABASE_URL` below).

**1. Backend**

```bash
cd backend
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env   # Windows: copy .env.example .env
```

Edit `backend/.env` so `DATABASE_URL` matches your local Postgres admin user/password
(the default `postgres:postgres@localhost:5432` only works if that's actually what you
set up). Then create the database itself — this is the step that's easy to miss, and
what throws `database "pricewatch" does not exist` if skipped:

```bash
python scripts/setup_local_db.py
```

This only creates the database (assumes the role in `DATABASE_URL` already exists,
which is true for a normal Postgres install) and is safe to re-run.

Now start the API:

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

On startup it creates its own tables (no migrations yet) and starts the price-check
scheduler in-process.

**2. Frontend**

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env   # defaults to VITE_API_URL=http://localhost:8000
npm run dev
```

- App: http://localhost:3000 (landing page at `/`, dashboard at `/app`)

Add a watch from the UI at http://localhost:3000/app/new, or directly against the API:

```bash
curl -X POST http://localhost:8000/watches \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example product",
    "url": "https://example.com/product/123",
    "css_selector": ".price",
    "notify_email": "you@example.com",
    "check_interval_minutes": 60
  }'
```

SMTP is optional for local testing — without it configured, checks and price history
still work, email sending just fails (logged, doesn't crash anything).

## Running with Docker (for later)

Once everything above is confirmed working locally, `docker-compose.yml` wires the same
three services together in containers:

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:3000 · Backend: http://localhost:8000 · Postgres: 5432

Note the frontend reads its backend URL from `PUBLIC_API_URL` at *runtime* (see
`frontend/server.js`), not at build time — that's what lets the same built image move
between environments later without a rebuild.

## Notes / known limitations (MVP)

- No auth — anyone who can reach the UI/API can manage watches. Fine for a personal demo,
  not for anything public yet.
- Price extraction is best-effort. Sites that render prices via JS (no plain HTML price
  text) won't work without a headless-browser fetch step — not implemented yet.
- No Alembic migrations yet; tables are created via `Base.metadata.create_all()` on
  startup. Fine for a demo, worth adding real migrations before this holds real data.
- SMTP is the only notification channel for now.

## Deployment

Not decided yet — once the demo works end-to-end, next step is picking the cheapest
place to run three small services (Node, FastAPI, Postgres) continuously.
