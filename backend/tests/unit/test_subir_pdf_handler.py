"""Tests unitarios del caso de uso de subida del PDF de una ficha.

El PDF es binario y NO se sanea (CLAUDE.md §10): se verifica que los bytes se almacenan tal
cual, que se fija el hash_pdf y que se crea una versión nueva (que captura el hash_pdf).
"""

from __future__ import annotations

from uuid import UUID

import pytest

from app.contexts.content.application.commands import SubirPdfContenidoCommand
from app.contexts.content.application.handlers import SubirPdfContenidoHandler
from app.contexts.content.domain.model import ContentVersion, Contenido, TipoContenido
from app.shared.domain.base import DomainError, NotFoundError


class _FakeRepo:
    def __init__(self, contenido: Contenido | None) -> None:
        self._contenido = contenido
        self.saved = False

    def get(self, contenido_id: UUID) -> Contenido | None:
        return self._contenido

    def save(self, contenido: Contenido) -> None:
        self.saved = True


class _FakeVersionRepo:
    def __init__(self) -> None:
        self.versions: list[ContentVersion] = []

    def list_for_contenido(self, contenido_id: UUID) -> list[ContentVersion]:
        return list(self.versions)

    def add(self, version: ContentVersion) -> None:
        self.versions.append(version)


class _FakeUoW:
    def __init__(self) -> None:
        self.committed = False

    def commit(self) -> None:
        self.committed = True


class _FakeStorage:
    """Devuelve los bytes recibidos para poder verificar que no se transforman."""

    def __init__(self) -> None:
        self.saved_bytes: bytes | None = None

    def save(self, raw_pdf: bytes) -> str:
        self.saved_bytes = raw_pdf
        return "b" * 64

    def url_for(self, file_hash: str) -> str:
        return f"/ficha/{file_hash}.pdf"


def test_subir_pdf_almacena_sin_modificar_y_fija_hash() -> None:
    contenido = Contenido(titulo="Ficha", tipo=TipoContenido.PDF)
    repo, vrepo, uow, storage = _FakeRepo(contenido), _FakeVersionRepo(), _FakeUoW(), _FakeStorage()
    handler = SubirPdfContenidoHandler(repo, vrepo, uow, storage)  # type: ignore[arg-type]

    raw = b"%PDF-1.7\n...bytes binarios..."
    dto = handler.handle(
        SubirPdfContenidoCommand(contenido_id=contenido.id, editor_id=contenido.id, raw_pdf=raw)
    )

    assert storage.saved_bytes == raw  # bytes intactos
    assert dto.hash_pdf == "b" * 64
    assert repo.saved is True
    assert uow.committed is True
    assert len(vrepo.versions) == 1
    assert vrepo.versions[0].hash_pdf == "b" * 64  # la versión captura el PDF


def test_subir_pdf_a_tipo_texto_lanza_domain_error() -> None:
    contenido = Contenido(titulo="Articulo", tipo=TipoContenido.TEXTO)
    handler = SubirPdfContenidoHandler(
        _FakeRepo(contenido), _FakeVersionRepo(), _FakeUoW(), _FakeStorage()  # type: ignore[arg-type]
    )
    with pytest.raises(DomainError):
        handler.handle(
            SubirPdfContenidoCommand(
                contenido_id=contenido.id, editor_id=contenido.id, raw_pdf=b"%PDF-1.7"
            )
        )


def test_subir_pdf_a_inexistente_lanza_not_found() -> None:
    handler = SubirPdfContenidoHandler(
        _FakeRepo(None), _FakeVersionRepo(), _FakeUoW(), _FakeStorage()  # type: ignore[arg-type]
    )
    with pytest.raises(NotFoundError):
        handler.handle(
            SubirPdfContenidoCommand(
                contenido_id=UUID(int=0), editor_id=UUID(int=0), raw_pdf=b"%PDF-1.7"
            )
        )
