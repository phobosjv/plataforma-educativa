#!/bin/sh
# Entrypoint del backend: baja privilegios + migraciones + seed admin si no existe + arranque.
set -e

# Endurecimiento (menor privilegio): el contenedor arranca como root SOLO para ajustar el
# propietario de los volúmenes montados (./data y ./media) y, acto seguido, se reinvoca a sí
# mismo bajando privilegios a `appuser` con gosu. Así las migraciones, el seed y uvicorn
# corren SIN privilegios (reduce el daño si hubiera una RCE). Patrón estándar (cf. la imagen
# oficial de postgres). En la segunda pasada (ya como appuser) este bloque se omite.
if [ "$(id -u)" = "0" ]; then
  echo "[entrypoint] Ajustando permisos de /app/data y /app/media y bajando privilegios a appuser…"
  chown -R appuser:appuser /app/data /app/media 2>/dev/null || true
  exec gosu appuser "$0" "$@"
fi

echo "[entrypoint] Aplicando migraciones Alembic…"
alembic upgrade head

echo "[entrypoint] Comprobando usuario administrador…"
python - <<'EOF'
import sys
import app.bootstrap  # noqa: F401 — registra modelos ORM

from app.contexts.identity.application.commands import CrearUsuarioCommand
from app.contexts.identity.application.handlers import CrearUsuarioHandler
from app.contexts.identity.infrastructure.auth_service import ArgonAuthService
from app.contexts.identity.infrastructure.repositories import SqlAlchemyUsuarioRepository
from app.config import settings
from app.shared.domain.base import DomainError
from app.shared.infrastructure.database import SessionLocal
from app.shared.infrastructure.unit_of_work import UnitOfWork

session = SessionLocal()
try:
    repo = SqlAlchemyUsuarioRepository(session)
    if repo.list_all():
        print("[entrypoint] Ya existe al menos un usuario. No se crea el admin por defecto.")
        sys.exit(0)

    email = settings.default_admin_email
    password = settings.default_admin_password

    auth = ArgonAuthService(
        secret_key=settings.secret_key,
        expire_minutes=settings.access_token_expire_minutes,
    )
    uow = UnitOfWork(session)
    handler = CrearUsuarioHandler(repo=repo, auth=auth, uow=uow)
    handler.handle(CrearUsuarioCommand(email=email, password=password, rol="admin"))
    print(f"[entrypoint] Usuario admin creado: {email}")
    print("[entrypoint] AVISO: cambia la contraseña tras el primer acceso.")
finally:
    session.close()
EOF

echo "[entrypoint] Arrancando servidor…"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
