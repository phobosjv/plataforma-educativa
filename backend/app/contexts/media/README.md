# Contexto: media

Capas: `domain` (puro) · `application` (casos de uso, CQRS) · `infrastructure` (adapters) · `api` (routers).
Regla de dependencia: api/infrastructure → application → domain. El dominio no conoce frameworks.
Ver responsabilidades en `docs/ARCHITECTURE.md`.
