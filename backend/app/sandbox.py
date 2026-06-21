"""Servidor del ORIGEN SANDBOX (CLAUDE.md §10 / ARCHITECTURE AD-3).

App ASGI **independiente** de la API: sirve los HTML de ejercicios interactivos desde un
origen distinto al de la aplicación, con CSP estricta, para que el JS arbitrario del
ejercicio quede aislado del CMS.

- En **dev** se ejecuta aparte:  ``uvicorn app.sandbox:sandbox_app --port 8002``
- En **prod** el mismo contenido lo sirve ``nginx/sandbox.conf`` desde ``sandbox.<dominio>``.

IMPORTANTE: la CSP de aquí (``SANDBOX_CSP``) y la de ``nginx/sandbox.conf`` son dos fuentes
que DEBEN mantenerse sincronizadas. Si cambias una, cambia la otra.
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response

from app.config import settings

_HASH_RE = re.compile(r"^[0-9a-f]{64}$")

# Política de seguridad del contenido. El ejercicio puede ejecutar su propio JS/CSS inline
# (es HTML autocontenido), pero NO puede llamar a casa (``connect-src 'none'``) ni navegar
# fuera. ``frame-ancestors`` restringe quién puede embeber el iframe (los orígenes de la app).
def _build_csp() -> str:
    app_origins = " ".join(o.strip() for o in settings.app_origins.split(",") if o.strip())
    frame_ancestors = app_origins or "'none'"
    return (
        "default-src 'none'; "
        "script-src 'unsafe-inline'; "
        "style-src 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self' data:; "
        "media-src 'self' data:; "
        "connect-src 'none'; "
        "base-uri 'none'; "
        "form-action 'none'; "
        f"frame-ancestors {frame_ancestors}"
    )


SANDBOX_CSP = _build_csp()

_SECURITY_HEADERS = {
    "Content-Security-Policy": SANDBOX_CSP,
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    # Content-addressed e inmutable: cachear agresivamente es seguro.
    "Cache-Control": "public, max-age=31536000, immutable",
}

sandbox_app = FastAPI(title="Plataforma Educativa — Sandbox", version="0.6.0")


@sandbox_app.get("/health", tags=["infra"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "sandbox"}


@sandbox_app.get("/ejercicio/{file_hash}", response_class=HTMLResponse)
def servir_ejercicio(file_hash: str) -> HTMLResponse:
    if not _HASH_RE.match(file_hash):
        raise HTTPException(status_code=400, detail="Hash de ejercicio inválido.")
    ruta = Path(settings.media_dir) / file_hash[:2] / f"{file_hash}.html"
    if not ruta.is_file():
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado.")
    return HTMLResponse(content=ruta.read_bytes(), headers=_SECURITY_HEADERS)


def _nombre_descarga_seguro(nombre: str | None) -> str:
    """Filtra el nombre de descarga para que sea seguro en Content-Disposition.

    Solo letras/dígitos/espacio/guion/guion bajo/punto; el resto se descarta (evita inyección
    de cabecera). Si queda vacío, usa "ficha.pdf".
    """
    if not nombre:
        return "ficha.pdf"
    limpio = "".join(c for c in nombre if c.isalnum() or c in " -_.").strip()
    return limpio[:100] or "ficha.pdf"


@sandbox_app.get("/ficha/{file_hash}.pdf")
def servir_ficha_pdf(file_hash: str, descargar: int = 0, nombre: str | None = None) -> Response:
    """Sirve una ficha PDF content-addressed desde el origen sandbox.

    Por defecto se muestra embebida (``inline``) para el visor del navegador en la ficha pública.
    Con ``?descargar=1`` se fuerza la descarga (``attachment``) con un nombre amigable, para que
    familias y alumnado puedan imprimir la ficha y escribir sobre el papel.
    """
    if not _HASH_RE.match(file_hash):
        raise HTTPException(status_code=400, detail="Hash de ficha inválido.")
    ruta = Path(settings.media_dir) / file_hash[:2] / f"{file_hash}.pdf"
    if not ruta.is_file():
        raise HTTPException(status_code=404, detail="Ficha no encontrada.")
    if descargar:
        disposition = f'attachment; filename="{_nombre_descarga_seguro(nombre)}"'
    else:
        disposition = "inline"
    headers = {**_SECURITY_HEADERS, "Content-Disposition": disposition}
    return Response(content=ruta.read_bytes(), media_type="application/pdf", headers=headers)
