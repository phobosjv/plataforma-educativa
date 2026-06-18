"""Repositorios SQLAlchemy del contexto CONTENIDO."""

from __future__ import annotations

import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.contexts.content.domain.model import ContentVersion, Contenido, TipoContenido
from app.contexts.content.infrastructure.fts import construir_match
from app.contexts.content.infrastructure.models import ContentVersionModel, ContenidoModel


class SqlAlchemyContenidoRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, contenido: Contenido) -> None:
        self._session.add(self._to_model(contenido))

    def get(self, contenido_id: UUID) -> Contenido | None:
        model = self._session.get(ContenidoModel, str(contenido_id))
        return self._to_domain(model) if model else None

    def save(self, contenido: Contenido) -> None:
        model = self._session.get(ContenidoModel, str(contenido.id))
        if model is None:
            return
        model.titulo = contenido.titulo
        model.descripcion = contenido.descripcion
        model.is_published = contenido.publicado
        model.is_deleted = contenido.borrado
        model.is_exam = contenido.es_examen
        model.ciclo_id = str(contenido.ciclo_id) if contenido.ciclo_id else None
        model.curso_id = str(contenido.curso_id) if contenido.curso_id else None
        model.asignatura_id = str(contenido.asignatura_id) if contenido.asignatura_id else None
        model.body_html = contenido.body_html
        model.hash_html = contenido.hash_html
        model.tags_json = json.dumps(contenido.etiquetas, ensure_ascii=False)
        model.updated_at = contenido.updated_at

    def list_published(self) -> list[Contenido]:
        stmt = (
            select(ContenidoModel)
            .where(ContenidoModel.is_published.is_(True))
            .where(ContenidoModel.is_deleted.is_(False))
            .order_by(ContenidoModel.updated_at.desc())
        )
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars()]

    def list_all(self) -> list[Contenido]:
        stmt = (
            select(ContenidoModel)
            .where(ContenidoModel.is_deleted.is_(False))
            .order_by(ContenidoModel.updated_at.desc())
        )
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars()]

    def list_trash(self) -> list[Contenido]:
        stmt = (
            select(ContenidoModel)
            .where(ContenidoModel.is_deleted.is_(True))
            .order_by(ContenidoModel.updated_at.desc())
        )
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars()]

    def list_trash_borrado_antes_de(self, limite: datetime) -> list[Contenido]:
        """Contenido en papelera que entró antes de ``limite``.

        Un contenido borrado está congelado (no se edita ni republica), por lo que su
        ``updated_at`` es el instante en que se movió a la papelera. Sirve, pues, como
        marca de "borrado en" para decidir la antigüedad de la purga programada.
        """
        stmt = (
            select(ContenidoModel)
            .where(ContenidoModel.is_deleted.is_(True))
            .where(ContenidoModel.updated_at < limite)
            .order_by(ContenidoModel.updated_at)
        )
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars()]

    def buscar(self, texto: str, solo_publicados: bool = True) -> list[Contenido]:
        """Búsqueda full-text por título/descripción/etiquetas (FTS5), ordenada por relevancia.

        Une el índice ``content_fts`` con ``content`` por ``rowid`` para aplicar la
        visibilidad (no borrados; publicados si procede) y ordena por ``rank`` (mejor
        relevancia primero). Devuelve a lo sumo 50 resultados. Si el texto no tiene
        términos válidos, devuelve lista vacía sin tocar la BD.
        """
        match = construir_match(texto)
        if not match:
            return []
        filtro_pub = "AND c.is_published = 1" if solo_publicados else ""
        stmt = text(
            f"""
            SELECT c.id
            FROM content_fts
            JOIN content c ON c.rowid = content_fts.rowid
            WHERE content_fts MATCH :match
              AND c.is_deleted = 0
              {filtro_pub}
            ORDER BY rank
            LIMIT 50
            """
        )
        ids = self._session.execute(stmt, {"match": match}).scalars().all()
        # Cargamos los modelos preservando el orden por relevancia que dio FTS5.
        resultados: list[Contenido] = []
        for cid in ids:
            model = self._session.get(ContenidoModel, cid)
            if model is not None:
                resultados.append(self._to_domain(model))
        return resultados

    def delete_permanent(self, contenido_id: UUID) -> None:
        model = self._session.get(ContenidoModel, str(contenido_id))
        if model:
            self._session.delete(model)

    @staticmethod
    def _to_domain(model: ContenidoModel) -> Contenido:
        return Contenido(
            id=UUID(model.id),
            titulo=model.titulo,
            descripcion=model.descripcion,
            autor_id=UUID(model.autor_id) if model.autor_id else None,
            tipo=TipoContenido(model.tipo),
            ciclo_id=UUID(model.ciclo_id) if model.ciclo_id else None,
            curso_id=UUID(model.curso_id) if model.curso_id else None,
            asignatura_id=UUID(model.asignatura_id) if model.asignatura_id else None,
            idioma=model.idioma,
            etiquetas=json.loads(model.tags_json),
            publicado=model.is_published,
            borrado=model.is_deleted,
            es_examen=model.is_exam,
            hash_html=model.hash_html,
            body_html=model.body_html,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(contenido: Contenido) -> ContenidoModel:
        return ContenidoModel(
            id=str(contenido.id),
            tipo=contenido.tipo.value,
            titulo=contenido.titulo,
            descripcion=contenido.descripcion,
            autor_id=str(contenido.autor_id) if contenido.autor_id else None,
            ciclo_id=str(contenido.ciclo_id) if contenido.ciclo_id else None,
            curso_id=str(contenido.curso_id) if contenido.curso_id else None,
            asignatura_id=str(contenido.asignatura_id) if contenido.asignatura_id else None,
            idioma=contenido.idioma,
            is_published=contenido.publicado,
            is_deleted=contenido.borrado,
            is_exam=contenido.es_examen,
            hash_html=contenido.hash_html,
            body_html=contenido.body_html,
            tags_json=json.dumps(contenido.etiquetas, ensure_ascii=False),
            created_at=contenido.created_at,
            updated_at=contenido.updated_at,
        )


class SqlAlchemyContenidoEnTaxonomia:
    """Adapter del puerto ``taxonomy.ContenidoEnTaxonomia``: cuenta contenidos por taxonomía.

    Cuenta TODO el contenido no purgado (incluida la papelera): un contenido en papelera puede
    restaurarse, así que su referencia a curso/asignatura sigue vigente e impide borrar esa
    taxonomía y dejar la referencia colgando (SQLite no fuerza las claves foráneas).
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def cuenta_por_curso(self, curso_id: UUID) -> int:
        return self._contar(ContenidoModel.curso_id == str(curso_id))

    def cuenta_por_asignatura(self, asignatura_id: UUID) -> int:
        return self._contar(ContenidoModel.asignatura_id == str(asignatura_id))

    def _contar(self, condicion: object) -> int:
        stmt = select(func.count()).select_from(ContenidoModel).where(condicion)
        return int(self._session.execute(stmt).scalar_one())


class SqlAlchemyContentVersionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, version: ContentVersion) -> None:
        self._session.add(
            ContentVersionModel(
                id=str(version.id),
                content_id=str(version.contenido_id),
                version_no=version.version_no,
                metadata_snapshot_json=json.dumps(version.metadata_snapshot, ensure_ascii=False),
                body_html=version.body_html,
                hash_html=version.hash_html,
                created_by=str(version.created_by),
                created_at=version.created_at,
            )
        )

    def list_for_contenido(self, contenido_id: UUID) -> list[ContentVersion]:
        stmt = (
            select(ContentVersionModel)
            .where(ContentVersionModel.content_id == str(contenido_id))
            .order_by(ContentVersionModel.version_no)
        )
        return [
            ContentVersion(
                id=UUID(m.id),
                contenido_id=UUID(m.content_id),
                version_no=m.version_no,
                metadata_snapshot=json.loads(m.metadata_snapshot_json),
                body_html=m.body_html,
                hash_html=m.hash_html,
                created_by=UUID(m.created_by),
                created_at=m.created_at,
            )
            for m in self._session.execute(stmt).scalars()
        ]
