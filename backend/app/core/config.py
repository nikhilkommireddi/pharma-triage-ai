from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "PharmaTriage AI"
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg://pharmatriage:pharmatriage@localhost:5432/pharmatriage"

    api_cors_origins: list[str] = ["http://localhost:5173"]

    storage_dir: str = "./data/uploads"
    max_upload_size_bytes: int = 10 * 1024 * 1024

    anthropic_api_key: str | None = None
    extraction_model: str = "claude-sonnet-5"


@lru_cache
def get_settings() -> Settings:
    return Settings()
