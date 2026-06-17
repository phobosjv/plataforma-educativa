"""Composición de dependencias: registra los modelos ORM con Base y expone factories."""

from __future__ import annotations

# Importaciones de efecto lateral: registran los modelos ORM con Base.metadata.
# Deben estar antes de cualquier uso de Base.metadata (migraciones, create_all en tests).
import app.contexts.identity.infrastructure.models  # noqa: F401
import app.contexts.content.infrastructure.models  # noqa: F401
import app.contexts.taxonomy.infrastructure.models  # noqa: F401
import app.contexts.configuration.infrastructure.models  # noqa: F401
import app.contexts.analytics.infrastructure.models  # noqa: F401
