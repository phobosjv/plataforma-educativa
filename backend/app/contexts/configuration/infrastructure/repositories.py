from __future__ import annotations

from sqlalchemy.orm import Session

from app.contexts.configuration.domain.model import (
    SINGLETON_ID,
    ConfiguracionSitio,
)
from app.contexts.configuration.infrastructure.models import ConfiguracionModel


class SqlAlchemyConfiguracionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self) -> ConfiguracionSitio:
        model = self._session.get(ConfiguracionModel, str(SINGLETON_ID))
        if model is None:
            model = ConfiguracionModel(
                id=str(SINGLETON_ID),
                nombre_sitio="Plataforma Educativa",
                paleta_activa="cielo",
                paletas_json="[]",
            )
            self._session.add(model)
        return self._to_domain(model)

    def save(self, config: ConfiguracionSitio) -> None:
        model = self._session.get(ConfiguracionModel, str(config.id))
        if model is None:
            model = ConfiguracionModel(id=str(config.id))
            self._session.add(model)
        model.nombre_sitio = config.nombre_sitio
        model.paleta_activa = config.paleta_activa
        model.paletas_json = config.paletas_json

    @staticmethod
    def _to_domain(m: ConfiguracionModel) -> ConfiguracionSitio:
        return ConfiguracionSitio(
            id=SINGLETON_ID,
            nombre_sitio=m.nombre_sitio,
            paleta_activa=m.paleta_activa,
            paletas_json=m.paletas_json,
        )
