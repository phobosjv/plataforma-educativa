"""Generación de los iconos de la PWA (instalación en móvil/escritorio).

El icono se deriva de la configuración del sitio:
- Si hay **logo** subido en administración, se usa el logo centrado sobre una baldosa blanca.
- Si **no** hay logo, se dibuja un icono genérico: baldosa con el color primario de la paleta
  activa y las **iniciales** del nombre del sitio en blanco.

Se generan dos *propósitos* (Web App Manifest):
- ``any``: el icono ocupa casi toda la baldosa (contextos que no recortan).
- ``maskable``: el contenido se mantiene dentro de la *zona segura* (~centro), porque el sistema
  operativo recorta el icono a un círculo/squircle. Por eso el icono anterior (un círculo blanco
  sólido a sangre con texto blanco encima, invisible) se veía como una circunferencia en blanco.

Infra pura (Pillow): no conoce FastAPI ni el dominio.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

_BLANCO = (255, 255, 255)


def _hex_a_rgb(valor: str) -> tuple[int, int, int]:
    """Convierte ``#rrggbb`` (o ``#rgb``) a una tupla RGB. Cae a un azul por defecto si falla."""
    s = valor.strip().lstrip("#")
    try:
        if len(s) == 3:
            s = "".join(c * 2 for c in s)
        if len(s) != 6:
            raise ValueError
        return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    except ValueError:
        return (2, 132, 199)  # #0284c7 (paleta "cielo")


def iniciales_de(nombre: str) -> str:
    """Hasta dos iniciales en mayúscula a partir del nombre del sitio."""
    palabras = [p for p in nombre.strip().split() if p]
    if not palabras:
        return "?"
    if len(palabras) == 1:
        return palabras[0][:2].upper()
    return (palabras[0][0] + palabras[1][0]).upper()


def _fuente(px: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Fuente escalable. ``load_default(size=)`` (Pillow >=10.1) no depende de fuentes del SO."""
    try:
        return ImageFont.load_default(size=px)
    except TypeError:  # Pillow muy antiguo: fuente bitmap fija (degradado aceptable)
        return ImageFont.load_default()


def generar_icono_png(
    size: int,
    *,
    maskable: bool,
    logo_path: Path | None,
    color_primario: str,
    iniciales: str,
) -> bytes:
    """Devuelve los bytes PNG del icono de la app para el tamaño y propósito dados."""
    # Fracción del lienzo que ocupa el contenido. En maskable se reduce para caber en la
    # zona segura del recorte del SO (la zona segura es el círculo interior del 80%).
    fraccion = 0.60 if maskable else 0.86
    contenido = max(1, int(size * fraccion))
    offset = (size - contenido) // 2

    if logo_path is not None:
        # Baldosa blanca + logo centrado (preservando proporción y transparencia).
        lienzo = Image.new("RGBA", (size, size), (*_BLANCO, 255))
        try:
            with Image.open(logo_path) as img:
                logo = img.convert("RGBA")
            logo.thumbnail((contenido, contenido), Image.LANCZOS)
            pos = ((size - logo.width) // 2, (size - logo.height) // 2)
            lienzo.paste(logo, pos, logo)  # usa el alfa del logo como máscara
            return _a_png(lienzo)
        except (OSError, ValueError) as e:
            logger.warning("No se pudo usar el logo %s como icono: %s", logo_path, e)
            # cae al genérico de abajo

    # Genérico: baldosa con el color de la paleta + iniciales en blanco.
    bg = _hex_a_rgb(color_primario)
    lienzo = Image.new("RGBA", (size, size), (*bg, 255))
    draw = ImageDraw.Draw(lienzo)
    texto = iniciales or "?"
    fuente = _fuente(int(contenido * 0.62))
    caja = draw.textbbox((0, 0), texto, font=fuente)
    tw, th = caja[2] - caja[0], caja[3] - caja[1]
    draw.text(
        (offset + (contenido - tw) // 2 - caja[0], offset + (contenido - th) // 2 - caja[1]),
        texto,
        fill=(*_BLANCO, 255),
        font=fuente,
    )
    return _a_png(lienzo)


def _a_png(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
