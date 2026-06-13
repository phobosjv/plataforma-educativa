"""Configuración por entorno (Twelve-Factor). Nada de valores incrustados."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/app.sqlite3"
    media_dir: str = "./media"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 120
    environment: str = "development"
    log_level: str = "INFO"
    cors_allow_origins: str = "http://localhost:5173"


settings = Settings()
