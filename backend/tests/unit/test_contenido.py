"""Ejemplo de test unitario del dominio (puro, sin I/O)."""

import pytest

from app.contexts.content.domain.model import Contenido, TipoContenido
from app.shared.domain.base import DomainError


def test_contenido_requiere_titulo():
    with pytest.raises(DomainError):
        Contenido(titulo="   ", tipo=TipoContenido.TEXTO)


def test_contenido_valido_se_crea():
    c = Contenido(titulo="Sumas 1", tipo=TipoContenido.INTERACTIVO)
    assert c.titulo == "Sumas 1"
