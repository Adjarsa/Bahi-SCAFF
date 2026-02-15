from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ScaffoldPlan AI API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    debug: bool = False

    database_url: str = "sqlite:///./scaffoldplan.db"
    allow_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    storage_dir: str = "storage"
    export_dir: str = "storage/exports"
    upload_dir: str = "storage/uploads"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allow_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
