from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Async Ingestion Service"
    debug: bool = False
    
    # Ingestion specific settings
    ingestion_timeout: int = 10
    ingestion_max_connections: int = 100
    ingestion_max_keepalive: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
