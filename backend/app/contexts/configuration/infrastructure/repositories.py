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
        model.fondo_activo = config.fondo_activo
        model.fondo_estilo = config.fondo_estilo
        model.logo_url = config.logo_url
        model.aula_abierta_label = config.aula_abierta_label
        model.aula_abierta_emoji = config.aula_abierta_emoji
        model.catalogo_titulo = config.catalogo_titulo
        model.catalogo_subtitulo = config.catalogo_subtitulo
        model.donaciones_json = config.donaciones_json
        model.redes_sociales_json = config.redes_sociales_json
        model.publicidad_activa = config.publicidad_activa
        model.publicidad_html_izquierda = config.publicidad_html_izquierda
        model.publicidad_html_derecha = config.publicidad_html_derecha

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
                fondo_activo="ninguno",
                fondo_estilo="ordenado",
                logo_url="",
                aula_abierta_label="Aula Abierta",
                aula_abierta_emoji="🌟",
                catalogo_titulo="¿En qué curso estás?",
                catalogo_subtitulo="Toca tu curso para ver las actividades",
                donaciones_json="[]",
                redes_sociales_json="[]",
                publicidad_activa=False,
                publicidad_html_izquierda="",
                publicidad_html_derecha="",
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
            fondo_activo=m.fondo_activo,
            fondo_estilo=m.fondo_estilo,
            logo_url=m.logo_url,
            aula_abierta_label=m.aula_abierta_label,
            aula_abierta_emoji=m.aula_abierta_emoji,
            catalogo_titulo=m.catalogo_titulo,
            catalogo_subtitulo=m.catalogo_subtitulo,
            donaciones_json=m.donaciones_json,
            redes_sociales_json=m.redes_sociales_json,
            publicidad_activa=m.publicidad_activa,
            publicidad_html_izquierda=m.publicidad_html_izquierda,
            publicidad_html_derecha=m.publicidad_html_derecha,
        )
