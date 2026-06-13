"""Buses CQRS mínimos (en proceso). Separan comandos (escritura) de consultas (lectura)."""

from __future__ import annotations

from typing import Any, Callable


class CommandBus:
    def __init__(self) -> None:
        self._handlers: dict[type, Callable[[Any], Any]] = {}

    def register(self, command_type: type, handler: Callable[[Any], Any]) -> None:
        self._handlers[command_type] = handler

    def dispatch(self, command: Any) -> Any:
        return self._handlers[type(command)](command)


class QueryBus:
    def __init__(self) -> None:
        self._handlers: dict[type, Callable[[Any], Any]] = {}

    def register(self, query_type: type, handler: Callable[[Any], Any]) -> None:
        self._handlers[query_type] = handler

    def ask(self, query: Any) -> Any:
        return self._handlers[type(query)](query)
