"""Repositorio SQLAlchemy del contexto IDENTITY."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.contexts.identity.domain.model import Rol, Usuario
from app.contexts.identity.infrastructure.models import UsuarioModel


class SqlAlchemyUsuarioRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, usuario: Usuario) -> None:
        self._session.add(self._to_model(usuario))

    def get_by_id(self, usuario_id: UUID) -> Usuario | None:
        model = self._session.get(UsuarioModel, str(usuario_id))
        return self._to_domain(model) if model else None

    def get_by_email(self, email: str) -> Usuario | None:
        stmt = select(UsuarioModel).where(UsuarioModel.email == email)
        model = self._session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None

    def list_all(self) -> list[Usuario]:
        stmt = select(UsuarioModel).order_by(UsuarioModel.created_at)
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars()]

    @staticmethod
    def _to_domain(model: UsuarioModel) -> Usuario:
        return Usuario(
            id=UUID(model.id),
            email=model.email,
            hashed_password=model.password_hash,
            rol=Rol(model.role),
            activo=model.is_active,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(usuario: Usuario) -> UsuarioModel:
        return UsuarioModel(
            id=str(usuario.id),
            email=usuario.email,
            password_hash=usuario.hashed_password,
            role=usuario.rol.value,
            is_active=usuario.activo,
            created_at=usuario.created_at,
        )
