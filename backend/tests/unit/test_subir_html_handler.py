"""Tests unitarios del caso de uso de subida de HTML de ejercicios interactivos.

El HTML de ejercicios NO se sanea (CLAUDE.md §10): aquí se verifica que los bytes se
almacenan tal cual, que se fija el hash y que se crea una versión nueva.
"""

from __future__ import annotations

from uuid import UUID

import pytest

from app.contexts.content.application.commands import SubirHtmlContenidoCommand
from app.contexts.content.application.handlers import SubirHtmlContenidoHandler
from app.contexts.content.domain.model import ContentVersion, Contenido, TipoContenido
from app.shared.domain.base import NotFoundError


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

    def save(self, raw_html: bytes) -> str:
        self.saved_bytes = raw_html
        return "f" * 64

    def url_for(self, file_hash: str) -> str:
        return f"/ejercicio/{file_hash}"


def test_subir_html_almacena_sin_sanear_y_fija_hash() -> None:
    contenido = Contenido(titulo="Juego", tipo=TipoContenido.INTERACTIVO)
    repo, vrepo, uow, storage = _FakeRepo(contenido), _FakeVersionRepo(), _FakeUoW(), _FakeStorage()
    handler = SubirHtmlContenidoHandler(repo, vrepo, uow, storage)  # type: ignore[arg-type]

    raw = b"<html><script>alert(1)</script></html>"
    dto = handler.handle(
        SubirHtmlContenidoCommand(contenido_id=contenido.id, editor_id=contenido.id, raw_html=raw)
    )

    assert storage.saved_bytes == raw  # NO se sanea: bytes intactos
    assert dto.hash_html == "f" * 64
    assert repo.saved is True
    assert uow.committed is True
    assert len(vrepo.versions) == 1
    assert vrepo.versions[0].hash_html == "f" * 64


def test_subir_html_a_tipo_texto_lanza_domain_error() -> None:
    from app.shared.domain.base import DomainError

    contenido = Contenido(titulo="Articulo", tipo=TipoContenido.TEXTO)
    handler = SubirHtmlContenidoHandler(
        _FakeRepo(contenido), _FakeVersionRepo(), _FakeUoW(), _FakeStorage()  # type: ignore[arg-type]
    )
    with pytest.raises(DomainError):
        handler.handle(
            SubirHtmlContenidoCommand(
                contenido_id=contenido.id, editor_id=contenido.id, raw_html=b"<html></html>"
            )
        )


def test_subir_html_a_inexistente_lanza_not_found() -> None:
    handler = SubirHtmlContenidoHandler(
        _FakeRepo(None), _FakeVersionRepo(), _FakeUoW(), _FakeStorage()  # type: ignore[arg-type]
    )
    with pytest.raises(NotFoundError):
        handler.handle(
            SubirHtmlContenidoCommand(
                contenido_id=UUID(int=0), editor_id=UUID(int=0), raw_html=b"<html></html>"
            )
        )
