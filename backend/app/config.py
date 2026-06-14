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
    # Origen aislado desde el que se sirven los HTML de ejercicios interactivos (§10).
    # En dev lo sirve `app.sandbox:sandbox_app` en :8002; en prod, `sandbox.<dominio>`.
    sandbox_base_url: str = "http://localhost:8002"
    # Orígenes de la app autorizados a embeber el iframe del sandbox (CSP frame-ancestors).
    app_origins: str = "http://localhost:5173"
    default_admin_email: str = "admin@plataforma.local"
    default_admin_password: str = "CambiaMe1234"


settings = Settings()
