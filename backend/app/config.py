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
    user_agent: str = (
        "Mozilla/5.0 (compatible; PriceWatchBot/1.0; +https://example.com/bot)"
    )


settings = Settings()
