from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Startup Navigator"
    app_env: str = "development"
    secret_key: str = Field(min_length=16)
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    database_url: str = "sqlite:///./startup_navigator.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    admin_email: str = "admin@example.com"
    admin_password: str = "ChangeMeAdmin123!"
    algorithm: str = "HS256"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
