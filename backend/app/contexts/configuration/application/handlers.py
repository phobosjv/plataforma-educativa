from __future__ import annotations

from app.contexts.configuration.application.commands import (
    ActivarPaletaCommand,
    ActualizarAjustesGeneralesCommand,
    ActualizarPaletaCommand,
    AgregarPaletaCommand,
    EliminarPaletaCommand,
)
from app.contexts.configuration.application.dtos import ConfiguracionDTO, config_to_dto
from app.contexts.configuration.domain.model import (
    EnlaceDonacion,
    EnlaceRedSocial,
    PaletaPersonalizada,
)
from app.contexts.configuration.domain.ports import ConfiguracionRepository
from app.shared.infrastructure.unit_of_work import UnitOfWork


class ObtenerConfiguracionHandler:
    def __init__(self, repo: ConfiguracionRepository) -> None:
        self._repo = repo

    def handle(self) -> ConfiguracionDTO:
        return config_to_dto(self._repo.get())


class ActualizarAjustesGeneralesHandler:
    def __init__(self, repo: ConfiguracionRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: ActualizarAjustesGeneralesCommand) -> ConfiguracionDTO:
        config = self._repo.get()
        config.cambiar_nombre(cmd.nombre_sitio)
        config.cambiar_fuente(cmd.fuente_activa)
        config.cambiar_fondo(cmd.fondo_activo)
        config.cambiar_estilo_fondo(cmd.fondo_estilo)
        config.cambiar_logo(cmd.logo_url)
        config.cambiar_aula_abierta(cmd.aula_abierta_label, cmd.aula_abierta_emoji)
        config.cambiar_textos_catalogo(cmd.catalogo_titulo, cmd.catalogo_subtitulo)
        config.cambiar_donaciones(
            [EnlaceDonacion(etiqueta=etq, url=url) for etq, url in cmd.donaciones]
        )
        config.cambiar_redes_sociales(
            [EnlaceRedSocial(red=red, url=url) for red, url in cmd.redes_sociales]
        )
        config.cambiar_publicidad(
            cmd.publicidad_activa, cmd.publicidad_html_izquierda, cmd.publicidad_html_derecha
        )
        self._repo.save(config)
        self._uow.commit()
        return config_to_dto(config)


class ActivarPaletaHandler:
    def __init__(self, repo: ConfiguracionRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: ActivarPaletaCommand) -> ConfiguracionDTO:
        config = self._repo.get()
        config.activar_paleta(cmd.paleta_id)
        self._repo.save(config)
        self._uow.commit()
        return config_to_dto(config)


class AgregarPaletaHandler:
    def __init__(self, repo: ConfiguracionRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: AgregarPaletaCommand) -> ConfiguracionDTO:
        config = self._repo.get()
        paleta = PaletaPersonalizada(
            id=cmd.id, nombre=cmd.nombre,
            bg=cmd.bg, surface=cmd.surface, fg=cmd.fg, primary=cmd.primary,
        )
        config.agregar_paleta(paleta)
        self._repo.save(config)
        self._uow.commit()
        return config_to_dto(config)


class ActualizarPaletaHandler:
    def __init__(self, repo: ConfiguracionRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: ActualizarPaletaCommand) -> ConfiguracionDTO:
        config = self._repo.get()
        paleta = PaletaPersonalizada(
            id=cmd.id, nombre=cmd.nombre,
            bg=cmd.bg, surface=cmd.surface, fg=cmd.fg, primary=cmd.primary,
        )
        config.actualizar_paleta(paleta)
        self._repo.save(config)
        self._uow.commit()
        return config_to_dto(config)


class EliminarPaletaHandler:
    def __init__(self, repo: ConfiguracionRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: EliminarPaletaCommand) -> ConfiguracionDTO:
        config = self._repo.get()
        config.eliminar_paleta(cmd.paleta_id)
        self._repo.save(config)
        self._uow.commit()
        return config_to_dto(config)
