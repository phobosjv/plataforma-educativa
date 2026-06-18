"""Motor SQLite, sesión y Base ORM compartida. Un solo Base para todo el proyecto."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _configurar_conexion(dbapi_conn: object, _: object) -> None:
    # WAL para lecturas concurrentes; foreign_keys=ON para que SQLite haga cumplir las claves
    # foráneas (las aplica por conexión y, por compatibilidad histórica, vienen desactivadas).
    cursor = dbapi_conn.cursor()  # type: ignore[union-attr]
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
