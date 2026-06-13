"""Tests unitarios del dominio TAXONOMÍA."""

import pytest

from app.contexts.taxonomy.domain.model import Asignatura, Ciclo, Curso
from app.shared.domain.base import DomainError


def test_ciclo_nombre_vacio_lanza_error():
    with pytest.raises(DomainError):
        Ciclo(nombre="")


def test_ciclo_nombre_espacios_lanza_error():
    with pytest.raises(DomainError):
        Ciclo(nombre="   ")


def test_ciclo_valido():
    c = Ciclo(nombre="Educación Infantil", orden=0)
    assert c.nombre == "Educación Infantil"
    assert c.orden == 0


def test_ciclo_actualizar():
    c = Ciclo(nombre="Infantil", orden=0)
    c.actualizar(nombre="1er Ciclo Primaria", orden=1)
    assert c.nombre == "1er Ciclo Primaria"
    assert c.orden == 1


def test_ciclo_actualizar_nombre_vacio_lanza_error():
    c = Ciclo(nombre="Infantil")
    with pytest.raises(DomainError):
        c.actualizar(nombre="")


def test_curso_sin_ciclo_lanza_error():
    with pytest.raises(DomainError):
        Curso(nombre="1º Primaria", ciclo_id=None)


def test_curso_nombre_vacio_lanza_error():
    from uuid import uuid4
    with pytest.raises(DomainError):
        Curso(nombre="", ciclo_id=uuid4())


def test_curso_valido():
    from uuid import uuid4
    cid = uuid4()
    c = Curso(nombre="1º Primaria", ciclo_id=cid, orden=1)
    assert c.nombre == "1º Primaria"
    assert c.ciclo_id == cid


def test_asignatura_nombre_vacio_lanza_error():
    with pytest.raises(DomainError):
        Asignatura(nombre="")


def test_asignatura_color_por_defecto():
    a = Asignatura(nombre="Matemáticas")
    assert a.color == "#6366f1"


def test_asignatura_actualizar():
    a = Asignatura(nombre="Lengua")
    a.actualizar(nombre="Lengua Castellana", color="#ef4444")
    assert a.nombre == "Lengua Castellana"
    assert a.color == "#ef4444"
