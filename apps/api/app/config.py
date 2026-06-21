from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PanelFlow API"
    storage_path: str = "/data/library"
    database_url: str = Field(
        default="postgresql://panelflow:change-me@postgres:5432/panelflow",
        validation_alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", validation_alias="REDIS_URL")
    suwayomi_url: str = Field(
        default="http://suwayomi:4567",
        validation_alias="SUWAYOMI_URL",
    )
    cors_origins: str = Field(default="http://localhost:3000", validation_alias="CORS_ORIGINS")
    admin_email: str = Field(validation_alias="ADMIN_EMAIL")
    admin_password: str = Field(validation_alias="ADMIN_PASSWORD")
    jwt_secret: str = Field(validation_alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_access_token_minutes: int = Field(default=60 * 12, validation_alias="JWT_ACCESS_TOKEN_MINUTES")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
