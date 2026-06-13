#!/usr/bin/env python
"""CLI para crear el primer usuario administrador en la base de datos.

Uso:
    python scripts/seed_admin.py                          # modo interactivo
    python scripts/seed_admin.py admin@ejemplo.com        # pide la contraseña
    python scripts/seed_admin.py admin@ejemplo.com Admin1234  # no interactivo

Ejecutar desde el directorio backend/:
    cd backend && python scripts/seed_admin.py
"""

from __future__ import annotations

import getpass
import sys
from pathlib import Path

# Asegurar que el paquete app es importable cuando se ejecuta desde backend/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app.bootstrap  # noqa: F401  — registra modelos ORM con Base.metadata
from app.contexts.identity.application.commands import CrearUsuarioCommand
from app.contexts.identity.application.handlers import CrearUsuarioHandler
from app.contexts.identity.infrastructure.auth_service import ArgonAuthService
from app.contexts.identity.infrastructure.repositories import SqlAlchemyUsuarioRepository
from app.config import settings
from app.shared.domain.base import DomainError
from app.shared.infrastructure.database import SessionLocal
from app.shared.infrastructure.unit_of_work import UnitOfWork


def main() -> None:
    args = sys.argv[1:]

    email = args[0] if len(args) >= 1 else input("Email del administrador: ").strip()
    if not email:
        print("Error: el email no puede estar vacío.", file=sys.stderr)
        sys.exit(1)

    if len(args) >= 2:
        password = args[1]
    else:
        password = getpass.getpass("Contraseña: ")
        confirm = getpass.getpass("Confirmar contraseña: ")
        if password != confirm:
            print("Error: las contraseñas no coinciden.", file=sys.stderr)
            sys.exit(1)

    if len(password) < 8:
        print("Error: la contraseña debe tener al menos 8 caracteres.", file=sys.stderr)
        sys.exit(1)

    session = SessionLocal()
    try:
        repo = SqlAlchemyUsuarioRepository(session)
        auth = ArgonAuthService(
            secret_key=settings.secret_key,
            expire_minutes=settings.access_token_expire_minutes,
        )
        uow = UnitOfWork(session)
        handler = CrearUsuarioHandler(repo=repo, auth=auth, uow=uow)

        usuario_id = handler.handle(
            CrearUsuarioCommand(email=email, password=password, rol="admin")
        )
        print(f"Usuario administrador creado: {email} (id={usuario_id})")
    except DomainError as exc:
        print(f"Error de dominio: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error inesperado: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
