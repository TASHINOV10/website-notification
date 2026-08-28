from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/pricewatch"

    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "notifications@pricewatch.local"
    smtp_use_tls: bool = True

    # How often the scheduler wakes up to see which watches are due for a check.
    scheduler_tick_seconds: int = 60
    default_check_interval_minutes: int = 60

    request_timeout_seconds: int = 15
    # A self-identifying bot UA (e.g. "PriceWatchBot/1.0") gets flat-out 403'd by
    # sites like OLX that block known bots -- a normal browser UA is what lets the
    # fetch through.
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )


settings = Settings()
