# PriceWatch

Track a product listing URL, get notified by email when the price changes. A minimal,
self-hostable take on [changedetection.io](https://changedetection.io/), scoped to price
tracking.

## Stack

- **Frontend**: Node.js + Express + EJS (server-rendered, no build step)
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
frontend/           Express + EJS UI, talks to the backend over HTTP
docker-compose.yml   postgres + backend + frontend, for local dev
```

## Running locally (Docker)

```bash
cp .env.example .env
# edit .env with real SMTP credentials if you want actual emails

docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API docs (Swagger): http://localhost:8000/docs
- Postgres: localhost:5432

Add a watch from the UI, or directly against the API:

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

## Running without Docker

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/pricewatch
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
BACKEND_URL=http://localhost:8000 npm run dev
```

You'll need a local Postgres running with a `pricewatch` database (or point
`DATABASE_URL` at whatever instance you have).

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
