"""Tests unitarios del ciclo de vida del dominio Contenido (puros, sin I/O)."""

import pytest

from app.contexts.content.domain.model import ContentVersion, Contenido, TipoContenido
from app.shared.domain.base import DomainError
from uuid import uuid4


def _contenido(titulo: str = "Test") -> Contenido:
    return Contenido(titulo=titulo, tipo=TipoContenido.TEXTO)


def test_contenido_requiere_titulo() -> None:
    with pytest.raises(DomainError):
        Contenido(titulo="   ", tipo=TipoContenido.TEXTO)


def test_contenido_valido_se_crea() -> None:
    c = _contenido("Sumas 1")
    assert c.titulo == "Sumas 1"
    assert c.publicado is False
    assert c.borrado is False


def test_publicar_contenido() -> None:
    c = _contenido()
    evento = c.publicar()
    assert c.publicado is True
    assert evento.contenido_id == c.id


def test_archivar_contenido() -> None:
    c = _contenido()
    c.publicar()
    c.archivar()
    assert c.publicado is False


def test_publicar_contenido_borrado_lanza_error() -> None:
    c = _contenido()
    c.borrar()
    with pytest.raises(DomainError):
        c.publicar()


def test_borrar_contenido() -> None:
    c = _contenido()
    c.publicar()
    evento = c.borrar()
    assert c.borrado is True
    assert c.publicado is False
    assert evento.contenido_id == c.id


def test_restaurar_contenido() -> None:
    c = _contenido()
    c.borrar()
    evento = c.restaurar()
    assert c.borrado is False
    assert evento.contenido_id == c.id


def test_content_version_es_inmutable() -> None:
    uid = uuid4()
    v = ContentVersion(
        contenido_id=uid,
        version_no=1,
        metadata_snapshot={"titulo": "v1"},
        created_by=uid,
    )
    with pytest.raises((AttributeError, TypeError)):
        v.version_no = 2  # type: ignore[misc]
