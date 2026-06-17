"""Índice de búsqueda full-text (FTS5) del contexto CONTENIDO.

La búsqueda del catálogo (CLAUDE.md §8) se apoya en una tabla virtual FTS5
``content_fts`` que indexa el título, la descripción y las etiquetas de cada
contenido. Es una tabla de *contenido externo* (``content='content'``): no
duplica los datos, sino que lee de la tabla ``content`` por ``rowid``. Se
mantiene **siempre** sincronizada mediante triggers (alta/baja/modificación),
de modo que el índice no depende de la ruta de escritura del repositorio.

El tokenizador ``unicode61 remove_diacritics 2`` normaliza acentos en ambos
sentidos (buscar "espana" encuentra "España" y viceversa), pensado para que un
niño de primaria encuentre lo que busca aunque no ponga tildes.

Este módulo centraliza el DDL para que lo usen por igual la migración de Alembic
y los tests de integración (que crean el esquema con ``Base.metadata.create_all``
y, por tanto, no pasan por las migraciones).
"""

from __future__ import annotations

import re
import sqlite3

# Columnas del contenido que se indexan. Deben llamarse EXACTAMENTE igual que las
# columnas de la tabla ``content`` (requisito de las tablas FTS5 de contenido externo).
_FTS_DDL: tuple[str, ...] = (
    "CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5("
    "  titulo, descripcion, tags_json,"
    "  content='content', content_rowid='rowid',"
    "  tokenize='unicode61 remove_diacritics 2'"
    ")",
    # Alta: replica la fila nueva en el índice.
    "CREATE TRIGGER IF NOT EXISTS content_fts_ai AFTER INSERT ON content BEGIN"
    "  INSERT INTO content_fts(rowid, titulo, descripcion, tags_json)"
    "  VALUES (new.rowid, new.titulo, new.descripcion, new.tags_json);"
    " END",
    # Baja: el comando especial 'delete' retira la fila del índice (contenido externo).
    "CREATE TRIGGER IF NOT EXISTS content_fts_ad AFTER DELETE ON content BEGIN"
    "  INSERT INTO content_fts(content_fts, rowid, titulo, descripcion, tags_json)"
    "  VALUES ('delete', old.rowid, old.titulo, old.descripcion, old.tags_json);"
    " END",
    # Modificación: retira la versión antigua e inserta la nueva.
    "CREATE TRIGGER IF NOT EXISTS content_fts_au AFTER UPDATE ON content BEGIN"
    "  INSERT INTO content_fts(content_fts, rowid, titulo, descripcion, tags_json)"
    "  VALUES ('delete', old.rowid, old.titulo, old.descripcion, old.tags_json);"
    "  INSERT INTO content_fts(rowid, titulo, descripcion, tags_json)"
    "  VALUES (new.rowid, new.titulo, new.descripcion, new.tags_json);"
    " END",
)

_DROP_DDL: tuple[str, ...] = (
    "DROP TRIGGER IF EXISTS content_fts_au",
    "DROP TRIGGER IF EXISTS content_fts_ad",
    "DROP TRIGGER IF EXISTS content_fts_ai",
    "DROP TABLE IF EXISTS content_fts",
)


def crear_indice_busqueda(conn: sqlite3.Connection) -> None:
    """Crea la tabla FTS5 y sus triggers, y vuelca el contenido ya existente.

    Idempotente: usa ``IF NOT EXISTS``. El comando ``'rebuild'`` rellena el índice
    a partir de las filas que ya hubiera en ``content`` (las creadas antes del índice).
    """
    for sentencia in _FTS_DDL:
        conn.execute(sentencia)
    conn.execute("INSERT INTO content_fts(content_fts) VALUES ('rebuild')")


def eliminar_indice_busqueda(conn: sqlite3.Connection) -> None:
    for sentencia in _DROP_DDL:
        conn.execute(sentencia)


_TOKEN = re.compile(r"\w+", re.UNICODE)


def construir_match(texto: str) -> str:
    """Convierte el texto del usuario en una consulta MATCH segura de FTS5.

    Cada palabra se entrecomilla (para neutralizar los operadores de FTS5, p. ej. ``-``
    o ``OR``, y evitar errores de sintaxis con lo que escriba un niño) y se le añade ``*``
    para buscar por prefijo. Los términos se combinan en AND implícito: ``mapa esp`` →
    ``"mapa"* "esp"*`` (deben aparecer ambos). Devuelve "" si no hay términos válidos.
    """
    tokens = _TOKEN.findall(texto)
    if not tokens:
        return ""
    return " ".join(f'"{t}"*' for t in tokens)
