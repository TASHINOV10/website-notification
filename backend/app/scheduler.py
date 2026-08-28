import datetime
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import PriceHistory, Watch
from app.notifier import send_price_change_email
from app.scraper import ScrapeError, check_price

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _is_due(watch: Watch, now: datetime.datetime) -> bool:
    if watch.last_checked_at is None:
        return True
    elapsed = now - watch.last_checked_at
    return elapsed >= datetime.timedelta(minutes=watch.check_interval_minutes)


def check_watch(db: Session, watch: Watch) -> None:
    now = datetime.datetime.utcnow()
    try:
        new_price = check_price(watch.url, watch.css_selector)
    except ScrapeError as exc:
        watch.last_error = str(exc)
        watch.last_checked_at = now
        db.commit()
        logger.warning("Watch %s failed: %s", watch.id, exc)
        return

    old_price = float(watch.last_price) if watch.last_price is not None else None

    db.add(PriceHistory(watch_id=watch.id, price=new_price, checked_at=now))
    watch.last_error = None
    watch.last_checked_at = now

    price_changed = old_price is not None and new_price != old_price
    watch.last_price = new_price
    db.commit()

    if price_changed:
        try:
            send_price_change_email(watch.notify_email, watch.name, watch.url, old_price, new_price)
        except Exception:
            logger.exception("Failed to notify watch %s", watch.id)


def run_due_checks() -> None:
    db = SessionLocal()
    try:
        now = datetime.datetime.utcnow()
        watches = db.query(Watch).filter(Watch.is_active.is_(True)).all()
        for watch in watches:
            if _is_due(watch, now):
                check_watch(db, watch)
    finally:
        db.close()


def start_scheduler() -> None:
    scheduler.add_job(
        run_due_checks,
        "interval",
        seconds=settings.scheduler_tick_seconds,
        id="run_due_checks",
        replace_existing=True,
    )
    scheduler.start()
