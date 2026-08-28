import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class WatchCreate(BaseModel):
    name: str | None = None
    url: HttpUrl
    css_selector: str | None = Field(
        default=None,
        description="Optional CSS selector pointing at the price element. "
        "If omitted, we try common price patterns/regex over the page.",
    )
    notify_email: EmailStr
    check_interval_minutes: int = Field(default=60, ge=5, le=10080)


class WatchUpdate(BaseModel):
    name: str | None = None
    css_selector: str | None = None
    notify_email: EmailStr | None = None
    check_interval_minutes: int | None = Field(default=None, ge=5, le=10080)
    is_active: bool | None = None


class PriceHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    price: float
    checked_at: datetime.datetime


class WatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str | None
    url: str
    css_selector: str | None
    notify_email: str
    check_interval_minutes: int
    is_active: bool
    last_price: float | None
    last_checked_at: datetime.datetime | None
    last_error: str | None
    created_at: datetime.datetime


class WatchDetailOut(WatchOut):
    price_history: list[PriceHistoryOut] = []
