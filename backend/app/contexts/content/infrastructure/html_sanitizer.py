"""Sanitizador del HTML de artículos de texto, basado en nh3 (ammonia).

Implementa el puerto ``HtmlSanitizer``. Mantiene una whitelist conservadora de
etiquetas y atributos seguros para artículos enriquecidos de un portal infantil:
sin scripts, sin estilos en línea peligrosos, sin iframes ni eventos ``on*``.
"""

from __future__ import annotations

import nh3

# Etiquetas permitidas en un artículo (encabezados, formato, listas, enlaces,
# imágenes, tablas y citas). Deliberadamente NO se permiten script/style/iframe.
_ALLOWED_TAGS: set[str] = {
    "p", "br", "hr", "span", "div",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "strong", "b", "em", "i", "u", "s", "mark", "sub", "sup", "small",
    "ul", "ol", "li",
    "blockquote", "pre", "code",
    "a", "img", "figure", "figcaption",
    "table", "thead", "tbody", "tr", "th", "td",
}

_ALLOWED_ATTRIBUTES: dict[str, set[str]] = {
    # "rel" lo gestiona nh3 vía link_rel (no debe ir en el allowlist).
    "a": {"href", "title", "target"},
    "img": {"src", "alt", "title", "width", "height"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan", "scope"},
    "*": {"class"},
}


class Nh3HtmlSanitizer:
    def sanitize(self, html: str) -> str:
        return nh3.clean(
            html,
            tags=_ALLOWED_TAGS,
            attributes=_ALLOWED_ATTRIBUTES,
            # Esquemas de URL permitidos: nada de javascript:
            url_schemes={"http", "https", "mailto"},
            link_rel="noopener noreferrer",
        )
