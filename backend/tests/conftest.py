"""Configuración global de la suite de tests.

Desactiva las tareas de mantenimiento en segundo plano (backups y purga de papelera)
durante los tests: el ``lifespan`` de FastAPI las arrancaría al usar ``TestClient`` como
context manager, y la purga operaría sobre la BD real de desarrollo (vía ``SessionLocal``),
no sobre la sesión SQLite en memoria de cada test. Los casos de uso de backup y purga se
prueban de forma aislada en sus propios tests unitarios.
"""

from __future__ import annotations

from app.config import settings

settings.backup_enabled = False
settings.trash_purge_enabled = False
# El volcado periódico de visitas opera sobre la BD real (SessionLocal); se desactiva en
# tests. El caso de uso de volcado se prueba aislado en sus propios tests.
settings.analytics_enabled = False
