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

    # --- Copias de seguridad de la BD (tarea en segundo plano) ---
    # Backup en caliente de SQLite (online backup API, seguro con WAL). Los ficheros
    # se rotan conservando solo los `backup_keep` más recientes.
    backup_enabled: bool = True
    backup_dir: str = "./data/backups"
    backup_interval_hours: int = 24
    backup_keep: int = 7
    # Copia incremental de la carpeta media (ejercicios HTML + imágenes) en cada ciclo de
    # backup. Los ficheros son content-addressed (inmutables): solo se copian los nuevos.
    # El espejo vive en `<backup_dir>/media`.
    media_backup_enabled: bool = True

    # --- Purga programada de la papelera (borrado lógico -> físico) ---
    # El contenido en papelera durante más de `trash_retention_days` se elimina de forma
    # DEFINITIVA por la tarea de mantenimiento. Poner `trash_purge_enabled=False` (o
    # `trash_retention_days<=0`) desactiva la purga automática.
    trash_purge_enabled: bool = True
    trash_retention_days: int = 30
    trash_purge_interval_hours: int = 24

    # --- Contador de visitas (agregación en memoria + volcado por lotes) ---
    # Las visitas se cuentan en un buffer en memoria y la tarea de mantenimiento las vuelca
    # a la BD cada `analytics_flush_interval_seconds` (CLAUDE.md §8: nunca una escritura por
    # petición). Visitas anónimas y agregadas (§10). Poner `analytics_enabled=False` desactiva
    # el volcado periódico (las visitas en buffer se persistirían al apagar la app).
    analytics_enabled: bool = True
    analytics_flush_interval_seconds: int = 300


settings = Settings()
