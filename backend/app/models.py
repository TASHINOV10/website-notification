import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Watch(Base):
    __tablename__ = "watches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    css_selector: Mapped[str] = mapped_column(String(1024), nullable=True)
    notify_email: Mapped[str] = mapped_column(String(255), nullable=False)

    check_interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    last_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    last_checked_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str] = mapped_column(String(2048), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    price_history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="watch", cascade="all, delete-orphan", order_by="PriceHistory.checked_at"
    )


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    watch_id: Mapped[int] = mapped_column(ForeignKey("watches.id", ondelete="CASCADE"))
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    checked_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    watch: Mapped["Watch"] = relationship(back_populates="price_history")
