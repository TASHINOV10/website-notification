from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Watch
from app.scheduler import check_watch
from app.schemas import WatchCreate, WatchDetailOut, WatchOut, WatchUpdate

router = APIRouter(prefix="/watches", tags=["watches"])


@router.get("", response_model=list[WatchOut])
def list_watches(db: Session = Depends(get_db)):
    return db.query(Watch).order_by(Watch.created_at.desc()).all()


@router.post("", response_model=WatchOut, status_code=201)
def create_watch(payload: WatchCreate, db: Session = Depends(get_db)):
    watch = Watch(
        name=payload.name,
        url=str(payload.url),
        css_selector=payload.css_selector,
        notify_email=payload.notify_email,
        check_interval_minutes=payload.check_interval_minutes,
    )
    db.add(watch)
    db.commit()
    db.refresh(watch)
    return watch


@router.get("/{watch_id}", response_model=WatchDetailOut)
def get_watch(watch_id: int, db: Session = Depends(get_db)):
    watch = db.get(Watch, watch_id)
    if watch is None:
        raise HTTPException(status_code=404, detail="Watch not found")
    return watch


@router.patch("/{watch_id}", response_model=WatchOut)
def update_watch(watch_id: int, payload: WatchUpdate, db: Session = Depends(get_db)):
    watch = db.get(Watch, watch_id)
    if watch is None:
        raise HTTPException(status_code=404, detail="Watch not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(watch, field, value)

    db.commit()
    db.refresh(watch)
    return watch


@router.delete("/{watch_id}", status_code=204)
def delete_watch(watch_id: int, db: Session = Depends(get_db)):
    watch = db.get(Watch, watch_id)
    if watch is None:
        raise HTTPException(status_code=404, detail="Watch not found")
    db.delete(watch)
    db.commit()


@router.post("/{watch_id}/check", response_model=WatchOut)
def trigger_check(watch_id: int, db: Session = Depends(get_db)):
    watch = db.get(Watch, watch_id)
    if watch is None:
        raise HTTPException(status_code=404, detail="Watch not found")
    check_watch(db, watch)
    db.refresh(watch)
    return watch
