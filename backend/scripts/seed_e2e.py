#!/usr/bin/env python
"""Siembra una base de datos determinista para los tests E2E (Playwright).

Crea, sobre una BD y una carpeta media AISLADAS (no las de desarrollo):
- un usuario admin,
- una taxonomía mínima (ciclo + curso + asignatura),
- un ejercicio interactivo publicado con un HTML que INTENTA escapar del sandbox
  (para el test de seguridad: el JS no debe alcanzar el origen padre),
- un artículo de texto publicado.

Las rutas se toman de las variables de entorno DATABASE_URL y MEDIA_DIR (las fija
playwright.config.ts). Si se ejecuta a mano, usa valores e2e por defecto.

La BD y la media se BORRAN al empezar para que cada ejecución parta de cero.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

# Aislar de los datos de desarrollo si no viene nada del entorno (ejecución manual).
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/e2e.sqlite3")
os.environ.setdefault("MEDIA_DIR", "./data/e2e-media")
os.environ.setdefault("SECRET_KEY", "e2e-secret-key-not-for-prod")

# Asegurar que el paquete `app` es importable al ejecutar desde backend/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ADMIN_EMAIL = "admin@e2e.local"
ADMIN_PASSWORD = "E2eTest1234"

# HTML autocontenido que intenta leer el origen padre. En un iframe sandbox sin
# allow-same-origin, acceder a window.parent.document lanza un SecurityError, así que
# `data-sandbox` debe quedar en "aislado". El test de seguridad lo comprueba.
EJERCICIO_HTML = b"""<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><title>Ejercicio E2E</title></head>
<body>
  <h1 id="titulo">Ejercicio interactivo E2E</h1>
  <p id="resultado-sandbox">pendiente</p>
  <script>
    var aislado = true;
    try {
      // Si NO estuviera aislado, esto leeria el documento del padre sin lanzar error.
      if (window.parent && window.parent.document && window.parent.location.href) {
        aislado = false;
      }
    } catch (e) {
      aislado = true; // SecurityError esperado => aislado correctamente.
    }
    var estado = aislado ? "aislado" : "fuga";
    document.getElementById("resultado-sandbox").textContent = estado;
    document.body.setAttribute("data-sandbox", estado);
  </script>
</body>
</html>
"""


def main() -> None:
    import app.bootstrap  # noqa: F401 — registra los modelos ORM con Base.metadata
    from app.config import settings
    from app.contexts.content.application.commands import (
        CrearContenidoCommand,
        PublicarContenidoCommand,
        SubirHtmlContenidoCommand,
    )
    from app.contexts.content.application.handlers import (
        CrearContenidoHandler,
        PublicarContenidoHandler,
        SubirHtmlContenidoHandler,
    )
    from app.contexts.content.infrastructure.html_sanitizer import Nh3HtmlSanitizer
    from app.contexts.content.infrastructure.html_storage import FileSystemHtmlStorage
    from app.contexts.content.infrastructure.repositories import (
        SqlAlchemyContenidoRepository,
        SqlAlchemyContentVersionRepository,
    )
    from app.contexts.identity.application.commands import CrearUsuarioCommand
    from app.contexts.identity.application.handlers import CrearUsuarioHandler
    from app.contexts.identity.infrastructure.auth_service import ArgonAuthService
    from app.contexts.identity.infrastructure.repositories import SqlAlchemyUsuarioRepository
    from app.contexts.taxonomy.application.commands import (
        CrearAsignaturaCommand,
        CrearCicloCommand,
        CrearCursoCommand,
    )
    from app.contexts.taxonomy.application.handlers import (
        CrearAsignaturaHandler,
        CrearCicloHandler,
        CrearCursoHandler,
    )
    from app.contexts.taxonomy.infrastructure.repositories import (
        SqlAlchemyAsignaturaRepository,
        SqlAlchemyCicloRepository,
        SqlAlchemyCursoRepository,
    )
    from app.shared.infrastructure.database import Base, SessionLocal, engine
    from app.shared.infrastructure.unit_of_work import UnitOfWork

    # 1. Partir de cero: borrar BD (fichero sqlite) y media del entorno e2e.
    db_path = Path(settings.database_url.replace("sqlite:///", ""))
    engine.dispose()
    for resto in (db_path, Path(f"{db_path}-wal"), Path(f"{db_path}-shm")):
        resto.unlink(missing_ok=True)
    media_dir = Path(settings.media_dir)
    if media_dir.exists():
        shutil.rmtree(media_dir)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    media_dir.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(engine)

    session = SessionLocal()
    try:
        auth = ArgonAuthService(settings.secret_key, settings.access_token_expire_minutes)

        # 2. Admin.
        admin_id = CrearUsuarioHandler(
            SqlAlchemyUsuarioRepository(session), auth, UnitOfWork(session)
        ).handle(CrearUsuarioCommand(email=ADMIN_EMAIL, password=ADMIN_PASSWORD, rol="admin"))

        # 3. Taxonomía (ciclo -> curso, + asignatura).
        ciclo_id = CrearCicloHandler(
            SqlAlchemyCicloRepository(session), UnitOfWork(session)
        ).handle(CrearCicloCommand(nombre="Primaria E2E"))
        curso_id = CrearCursoHandler(
            SqlAlchemyCursoRepository(session),
            SqlAlchemyCicloRepository(session),
            UnitOfWork(session),
        ).handle(CrearCursoCommand(nombre="3º E2E", ciclo_id=ciclo_id))
        asig_id = CrearAsignaturaHandler(
            SqlAlchemyAsignaturaRepository(session), UnitOfWork(session)
        ).handle(CrearAsignaturaCommand(nombre="Mates E2E"))

        repo = SqlAlchemyContenidoRepository(session)
        vrepo = SqlAlchemyContentVersionRepository(session)

        # 4. Ejercicio interactivo: crear, subir HTML, publicar.
        ejercicio_id = CrearContenidoHandler(repo, vrepo, UnitOfWork(session), Nh3HtmlSanitizer()).handle(
            CrearContenidoCommand(
                titulo="Ejercicio E2E",
                descripcion="Ejercicio interactivo de prueba E2E",
                tipo="interactivo",
                autor_id=admin_id,
                ciclo_id=ciclo_id,
                curso_id=curso_id,
                asignatura_id=asig_id,
            )
        )
        SubirHtmlContenidoHandler(
            repo, vrepo, UnitOfWork(session), FileSystemHtmlStorage(settings.media_dir)
        ).handle(
            SubirHtmlContenidoCommand(
                contenido_id=ejercicio_id, editor_id=admin_id, raw_html=EJERCICIO_HTML
            )
        )
        PublicarContenidoHandler(repo, UnitOfWork(session)).handle(
            PublicarContenidoCommand(contenido_id=ejercicio_id, published_by=admin_id)
        )

        # 5. Artículo de texto publicado.
        articulo_id = CrearContenidoHandler(repo, vrepo, UnitOfWork(session), Nh3HtmlSanitizer()).handle(
            CrearContenidoCommand(
                titulo="Artículo E2E",
                descripcion="Artículo de prueba E2E",
                tipo="texto",
                autor_id=admin_id,
                ciclo_id=ciclo_id,
                curso_id=curso_id,
                asignatura_id=asig_id,
                body_html="<p>Contenido del artículo de prueba E2E.</p>",
            )
        )
        PublicarContenidoHandler(repo, UnitOfWork(session)).handle(
            PublicarContenidoCommand(contenido_id=articulo_id, published_by=admin_id)
        )

        # 6. Asignatura TRANSVERSAL (Aula Abierta) + un contenido sin ciclo/curso.
        transversal_id = CrearAsignaturaHandler(
            SqlAlchemyAsignaturaRepository(session), UnitOfWork(session)
        ).handle(CrearAsignaturaCommand(nombre="Audición y Lenguaje", transversal=True))
        aula_id = CrearContenidoHandler(repo, vrepo, UnitOfWork(session), Nh3HtmlSanitizer()).handle(
            CrearContenidoCommand(
                titulo="Ejercicio Aula Abierta",
                descripcion="Contenido transversal de prueba E2E",
                tipo="texto",
                autor_id=admin_id,
                asignatura_id=transversal_id,
                body_html="<p>Actividad de apoyo (transversal).</p>",
            )
        )
        PublicarContenidoHandler(repo, UnitOfWork(session)).handle(
            PublicarContenidoCommand(contenido_id=aula_id, published_by=admin_id)
        )

        print(f"[seed_e2e] OK — admin={ADMIN_EMAIL} ejercicio={ejercicio_id} articulo={articulo_id}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
