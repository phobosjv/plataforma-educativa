"""Puerto del repositorio de configuración."""

from __future__ import annotations

from typing import Protocol

from app.contexts.configuration.domain.model import ConfiguracionSitio


class ConfiguracionRepository(Protocol):
    def get(self) -> ConfiguracionSitio: ...
    def save(self, config: ConfiguracionSitio) -> None: ...
