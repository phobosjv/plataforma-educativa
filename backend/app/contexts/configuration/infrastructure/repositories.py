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
        model = self._get_or_create_model()
        return self._to_domain(model)

    def save(self, config: ConfiguracionSitio) -> None:
        model = self._get_or_create_model()
        model.nombre_sitio = config.nombre_sitio
        model.paleta_activa = config.paleta_activa
        model.paletas_json = config.paletas_json
        model.fuente_activa = config.fuente_activa

    def _get_or_create_model(self) -> ConfiguracionModel:
        """Obtiene la fila singleton, creándola si no existe.

        El ``flush`` tras el ``add`` es imprescindible: convierte el objeto de
        pending a persistent y lo registra en el identity map, de modo que una
        segunda llamada (p. ej. ``get`` seguido de ``save`` en el mismo caso de
        uso) recupere la MISMA instancia en lugar de insertar un duplicado con
        el mismo id (lo que violaría la PK del singleton).
        """
        model = self._session.get(ConfiguracionModel, str(SINGLETON_ID))
        if model is None:
            model = ConfiguracionModel(
                id=str(SINGLETON_ID),
                nombre_sitio="Plataforma Educativa",
                paleta_activa="cielo",
                paletas_json="[]",
                fuente_activa="sistema",
            )
            self._session.add(model)
            self._session.flush()
        return model

    @staticmethod
    def _to_domain(m: ConfiguracionModel) -> ConfiguracionSitio:
        return ConfiguracionSitio(
            id=SINGLETON_ID,
            nombre_sitio=m.nombre_sitio,
            paleta_activa=m.paleta_activa,
            paletas_json=m.paletas_json,
            fuente_activa=m.fuente_activa,
        )
