"""Tests del generador de iconos de la PWA (app_icons)."""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

from app.shared.infrastructure.app_icons import generar_icono_png, iniciales_de


def _abrir(png: bytes) -> Image.Image:
    return Image.open(io.BytesIO(png)).convert("RGB")


def test_iniciales_dos_palabras() -> None:
    assert iniciales_de("Aprende y Juega") == "AY"


def test_iniciales_una_palabra() -> None:
    assert iniciales_de("Educativa") == "ED"


def test_iniciales_vacio() -> None:
    assert iniciales_de("   ") == "?"


def test_placeholder_usa_color_de_paleta_y_no_es_blob_blanco() -> None:
    """Regresión: el icono anterior salía como un círculo blanco sólido (texto invisible)."""
    png = generar_icono_png(
        192, maskable=True, logo_path=None, color_primario="#0284c7", iniciales="AY"
    )
    img = _abrir(png)
    assert img.size == (192, 192)
    # La esquina (fondo, a sangre) debe ser el color de la paleta, no blanco.
    assert img.getpixel((0, 0)) == (2, 132, 199)
    colores = img.getcolors(maxcolors=100000) or []
    total = 192 * 192
    blancos = sum(n for n, c in colores if c == (255, 255, 255))
    paleta = sum(
        n for n, c in colores
        if abs(c[0] - 2) < 24 and abs(c[1] - 132) < 24 and abs(c[2] - 199) < 24
    )
    # El fondo de paleta domina y las iniciales (blanco) son visibles pero minoritarias.
    assert paleta > total // 2
    assert 0 < blancos < paleta


def test_icono_con_logo_usa_baldosa_blanca(tmp_path: Path) -> None:
    # Logo: cuadrado magenta sólido.
    logo = tmp_path / "logo.png"
    Image.new("RGBA", (64, 64), (200, 0, 120, 255)).save(logo)

    png = generar_icono_png(
        192, maskable=False, logo_path=logo, color_primario="#0284c7", iniciales="AY"
    )
    img = _abrir(png)
    assert img.size == (192, 192)
    # Baldosa blanca: la esquina es blanca (el logo va centrado, no a sangre).
    assert img.getpixel((0, 0)) == (255, 255, 255)
    # El centro contiene el logo (magenta), no el color de la paleta ni blanco.
    centro = img.getpixel((96, 96))
    assert centro[0] > 150 and centro[2] > 80 and centro[1] < 80


def test_logo_ilegible_cae_al_generico(tmp_path: Path) -> None:
    falso = tmp_path / "roto.png"
    falso.write_bytes(b"esto no es una imagen")
    png = generar_icono_png(
        192, maskable=False, logo_path=falso, color_primario="#2e7d32", iniciales="AY"
    )
    img = _abrir(png)
    # Cae al genérico: fondo = color de paleta (verde bosque), no blanco.
    assert img.getpixel((0, 0)) == (46, 125, 50)


def test_maskable_deja_margen_de_zona_segura() -> None:
    """En maskable el contenido no llega a sangre: el borde es fondo limpio."""
    png = generar_icono_png(
        512, maskable=True, logo_path=None, color_primario="#0284c7", iniciales="AY"
    )
    img = _abrir(png)
    # Una banda cerca del borde superior central debe ser fondo (sin texto).
    assert img.getpixel((256, 8)) == (2, 132, 199)
