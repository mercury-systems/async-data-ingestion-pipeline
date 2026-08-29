"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Async Ingestion Pipeline"
    debug: bool = False
    ingestion_timeout: int = 10
    ingestion_max_connections: int = 100
    ingestion_max_keepalive: int = 20
    max_retries: int = 3
    retry_base_delay: float = 1.0
    max_retry_delay: float = 30.0
    batch_concurrency: int = 5
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 120
    job_db: str = "jobs.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
