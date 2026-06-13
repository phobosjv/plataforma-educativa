# -*- coding: utf-8 -*-
"""Descarga las fuentes self-hosted (subset latino, pesos 400 y 700) en
``frontend/public/fonts/`` usando la API de google-webfonts-helper.

Self-hosting (no CDN) para no exponer la IP de los menores a terceros (RGPD/DSA,
ver CLAUDE.md §10). Ejecutar una sola vez; los .woff2 se versionan en el repo.
"""
from __future__ import annotations

import json
import os
import urllib.request

API = "https://gwfh.mranftl.com/api/fonts/{fid}?subsets=latin&variants={variants}&formats=woff2"

# id gwfh -> (slug de salida, variantes a descargar)
FONTS = {
    "nunito": ("nunito", ["regular", "700"]),
    "quicksand": ("quicksand", ["regular", "700"]),
    "lexend": ("lexend", ["regular", "700"]),
    "atkinson-hyperlegible": ("atkinson", ["regular", "700"]),
    "andika": ("andika", ["regular", "700"]),
}

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public", "fonts")


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def download(url: str, dest: str) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    for fid, (slug, variants) in FONTS.items():
        meta = fetch_json(API.format(fid=fid, variants=",".join(variants)))
        by_variant = {v["id"]: v for v in meta["variants"]}
        for variant in variants:
            weight = "700" if variant == "700" else "400"
            v = by_variant.get(variant) or by_variant.get(weight)
            if not v or not v.get("woff2"):
                print(f"  ! {fid} {variant}: sin woff2")
                continue
            dest = os.path.join(OUT_DIR, f"{slug}-{weight}.woff2")
            size = download(v["woff2"], dest)
            print(f"  + {slug}-{weight}.woff2  ({size // 1024} KB)")


if __name__ == "__main__":
    main()
