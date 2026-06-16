"""Tests del servicio de copias de seguridad SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.shared.infrastructure.backup import SqliteBackupService


def _crear_bd(path: Path) -> None:
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
    con.execute("INSERT INTO t (v) VALUES ('hola')")
    con.commit()
    con.close()


def _servicio(tmp_path: Path, keep: int = 3) -> SqliteBackupService:
    db = tmp_path / "app.sqlite3"
    _crear_bd(db)
    return SqliteBackupService(f"sqlite:///{db}", str(tmp_path / "backups"), keep=keep)


def test_crear_backup_produce_copia_valida(tmp_path: Path) -> None:
    servicio = _servicio(tmp_path)

    info = servicio.crear_backup()

    copia = tmp_path / "backups" / info.nombre
    assert copia.exists()
    assert info.tamano_bytes > 0
    # La copia es una BD SQLite autónoma con los mismos datos del origen.
    con = sqlite3.connect(copia)
    assert con.execute("SELECT v FROM t").fetchone()[0] == "hola"
    con.close()


def test_listar_backups_ordena_de_reciente_a_antiguo(tmp_path: Path) -> None:
    servicio = _servicio(tmp_path)
    backups = tmp_path / "backups"
    backups.mkdir(parents=True, exist_ok=True)
    for marca in ("app-20200101-000000.sqlite3", "app-20200103-000000.sqlite3",
                  "app-20200102-000000.sqlite3"):
        (backups / marca).write_bytes(b"x")

    nombres = [b.nombre for b in servicio.listar_backups()]

    assert nombres == [
        "app-20200103-000000.sqlite3",
        "app-20200102-000000.sqlite3",
        "app-20200101-000000.sqlite3",
    ]


def test_rotacion_conserva_solo_las_n_mas_recientes(tmp_path: Path) -> None:
    servicio = _servicio(tmp_path, keep=3)
    backups = tmp_path / "backups"
    backups.mkdir(parents=True, exist_ok=True)
    # Cinco copias antiguas (fechas 2020) con nombres deterministas y distintos.
    for dia in range(1, 6):
        (backups / f"app-2020010{dia}-000000.sqlite3").write_bytes(b"viejo")

    # La copia nueva (fecha actual) entra y dispara la rotación a 3.
    info = servicio.crear_backup()

    restantes = sorted(p.name for p in backups.glob("app-*.sqlite3"))
    assert len(restantes) == 3
    # La copia recién creada (la más reciente por nombre) nunca se rota.
    assert info.nombre in restantes


def test_url_no_sqlite_es_rechazada(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        SqliteBackupService("postgresql://x/y", str(tmp_path), keep=1)


def test_ruta_de_devuelve_la_copia_existente(tmp_path: Path) -> None:
    servicio = _servicio(tmp_path)
    info = servicio.crear_backup()

    ruta = servicio.ruta_de(info.nombre)

    assert ruta is not None
    assert ruta.is_file()
    assert ruta.name == info.nombre


def test_ruta_de_inexistente_es_none(tmp_path: Path) -> None:
    servicio = _servicio(tmp_path)
    assert servicio.ruta_de("app-20200101-000000.sqlite3") is None


@pytest.mark.parametrize(
    "nombre",
    [
        "../app.sqlite3",
        "..\\app.sqlite3",
        "app-20200101-000000.sqlite3/../../etc/passwd",
        "/etc/passwd",
        "app.sqlite3",
        "app-2020-01.sqlite3",
        "otro.txt",
    ],
)
def test_ruta_de_rechaza_nombres_invalidos_y_traversal(tmp_path: Path, nombre: str) -> None:
    servicio = _servicio(tmp_path)
    assert servicio.ruta_de(nombre) is None
