"""Genera los iconos PWA placeholder (192×192 y 512×512 PNG).

Usa Pillow para dibujar un icono con fondo azul (#0284c7, paleta "cielo" por defecto)
y las iniciales "PE" en blanco. El admin puede reemplazar los ficheros por iconos propios.
"""
from __future__ import annotations

import os
import sys

BG_COLOR = (2, 132, 199)    # #0284c7 — cielo primary
FG_COLOR = (255, 255, 255)  # blanco


def _generate_pillow(out_dir: str) -> None:
    from PIL import Image, ImageDraw, ImageFont

    for size in (192, 512):
        img = Image.new("RGB", (size, size), BG_COLOR)
        draw = ImageDraw.Draw(img)

        # Círculo interior blanco semitransparente (decorativo)
        pad = size // 8
        draw.ellipse(
            [pad, pad, size - pad, size - pad],
            fill=(255, 255, 255, 30),
            outline=(255, 255, 255),
            width=max(2, size // 64),
        )

        # Texto "PE" centrado
        text = "PE"
        font_size = size // 3
        font: ImageFont.ImageFont | ImageFont.FreeTypeFont
        for path in (
            "arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        ):
            try:
                font = ImageFont.truetype(path, font_size)
                break
            except (OSError, IOError):
                continue
        else:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            ((size - tw) // 2 - bbox[0], (size - th) // 2 - bbox[1]),
            text,
            fill=FG_COLOR,
            font=font,
        )

        path_out = os.path.join(out_dir, f"icon-{size}.png")
        img.save(path_out, "PNG", optimize=True)
        print(f"  OK {path_out} ({size}x{size})")


def _generate_stdlib(out_dir: str) -> None:
    """Fallback: PNG sólido sin Pillow (solo stdlib)."""
    import struct
    import zlib

    r, g, b = BG_COLOR

    def chunk(name: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(name + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", crc)

    for size in (192, 512):
        raw = b"".join(b"\x00" + bytes([r, g, b]) * size for _ in range(size))
        png = (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b"")
        )
        path_out = os.path.join(out_dir, f"icon-{size}.png")
        with open(path_out, "wb") as f:
            f.write(png)
        print(f"  OK {path_out} ({size}x{size}, color solido)")


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(script_dir)
    out_dir = os.path.join(root, "frontend", "public", "icons")
    os.makedirs(out_dir, exist_ok=True)

    print("Generando iconos PWA...")
    try:
        _generate_pillow(out_dir)
    except ImportError:
        _generate_stdlib(out_dir)
    print("Listo.")


if __name__ == "__main__":
    main()
