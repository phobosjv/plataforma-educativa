# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.22.2.pdf usando fpdf2."""
from __future__ import annotations
import os
from fpdf import FPDF

PAGE_W = 210
MARGIN = 18
INNER_W = PAGE_W - 2 * MARGIN

INDIGO = (79, 70, 229)
INDIGO_LIGHT = (224, 231, 255)
GRAY_BG = (245, 247, 250)
BLACK = (30, 30, 30)
WHITE = (255, 255, 255)
GREEN = (22, 163, 74)

VERSION = "V-0.22.5"
FECHA = "2026-06-21"


class ManualPDF(FPDF):

    def header(self) -> None:
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*INDIGO)
        self.cell(0, 8, "Plataforma Educativa - Manual Tecnico y de Usuario  " + VERSION, align="L")
        self.set_text_color(*BLACK)
        self.ln(0)
        self.set_draw_color(*INDIGO)
        self.set_line_width(0.4)
        self.line(MARGIN, 14, PAGE_W - MARGIN, 14)
        self.ln(5)

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "Pagina " + str(self.page_no()) + "/{nb}", align="C")
        self.set_text_color(*BLACK)

    def cover(self) -> None:
        self.add_page()
        self.set_fill_color(*INDIGO)
        self.rect(0, 0, PAGE_W, 80, "F")
        self.set_y(18)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(*WHITE)
        self.cell(0, 12, "Plataforma Educativa", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 14)
        self.cell(0, 8, "CMS educativo interactivo para infantil y primaria", align="C",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "B", 16)
        self.set_y(58)
        self.cell(0, 10, "Manual Tecnico y de Usuario - " + VERSION, align="C",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*BLACK)
        self.set_y(88)
        self.set_font("Helvetica", "", 11)
        self.set_fill_color(*GRAY_BG)
        self.set_x(MARGIN)
        self.multi_cell(
            INNER_W, 6,
            "Arreglo DEFINITIVO del visor PDF. El badge de version confirmo que el frontend si se "
            "desplegaba, pero el worker seguia como application/octet-stream: su fichero conserva el "
            "mismo nombre entre versiones, asi que la respuesta vieja quedaba CACHEADA como immutable "
            "(1 año). Solucion: Vite emite el worker con extension .js (mapeada por defecto a "
            "application/javascript), lo que ademas cambia la URL y rompe la cache. Ya no depende de "
            "config especial de nginx.",
            border=0, fill=True,
        )
        self.ln(5)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Fecha: " + FECHA, align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, "Version del software: " + VERSION, align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, "Licencia: MIT (open source)", align="C")
        self.set_text_color(*BLACK)

    def chapter_title(self, num: str, title: str) -> None:
        self.ln(2)
        self.set_fill_color(*INDIGO)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 13)
        self.set_x(MARGIN)
        self.cell(INNER_W, 9, "  " + num + ". " + title, border=0, fill=True,
                  new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*BLACK)
        self.ln(3)

    def section(self, title: str) -> None:
        self.set_fill_color(*INDIGO_LIGHT)
        self.set_font("Helvetica", "B", 11)
        self.set_x(MARGIN)
        self.cell(INNER_W, 7, "  " + title, border=0, fill=True,
                  new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_x(MARGIN)
        self.multi_cell(INNER_W, 5.5, text)
        self.ln(2)

    def bullet(self, items: list) -> None:
        self.set_font("Helvetica", "", 10)
        for item in items:
            self.set_x(MARGIN + 6)
            self.cell(5, 5.5, "-")
            self.multi_cell(INNER_W - 11, 5.5, item)
        self.ln(1)

    def kv_table(self, rows: list) -> None:
        col1 = 70
        col2 = INNER_W - col1
        for i, (k, v) in enumerate(rows):
            fill = i % 2 == 0
            self.set_fill_color(245, 247, 250) if fill else self.set_fill_color(255, 255, 255)
            self.set_x(MARGIN)
            self.set_font("Helvetica", "B", 9)
            self.cell(col1, 6, "  " + k, border="LTB", fill=fill)
            self.set_font("Helvetica", "", 9)
            self.multi_cell(col2, 6, "  " + v, border="RTB", fill=fill)
        self.ln(3)


def build_pdf(output_path: str) -> None:
    pdf = ManualPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(MARGIN, 18, MARGIN)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.alias_nb_pages()

    pdf.cover()

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 10, "NOVEDADES DE " + VERSION, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("0", "El worker de PDF.js se emite como .js")
    pdf.section("Diagnostico (gracias al badge de version)")
    pdf.body(
        "El badge de version (v0.22.4) confirmo que el frontend SI se desplegaba, pero el worker "
        "seguia dando application/octet-stream. Causa doble: (1) el fichero del worker conserva el "
        "mismo nombre entre versiones (su contenido no cambia), asi que la respuesta vieja con MIME "
        "incorrecto quedaba CACHEADA como immutable (1 año); (2) depender de que nginx mapee .mjs es "
        "fragil entre despliegues."
    )
    pdf.section("Solucion: extension .js")
    pdf.bullet([
        "Vite emite el worker con extension .js (build.rollupOptions.output.assetFileNames).",
        ".js esta mapeada por defecto a application/javascript en cualquier nginx, sin config.",
        "Cambiar la extension cambia el nombre del fichero -> URL nueva -> rompe la cache envenenada.",
        "Se mantiene el manejo de .mjs/.wasm en nginx como red de seguridad, pero ya no es necesario.",
    ])
    pdf.section("Sobre servir el PDF desde el CMS")
    pdf.body(
        "No era necesario para este fallo: el error era del worker (asset del frontend), no del PDF "
        "(su URL del sandbox cargaba bien). Con PDF.js el PDF se dibuja en canvas sin ejecutar su JS "
        "embebido, asi que servirlo desde el CMS seria viable y mas simple, pero es una optimizacion "
        "aparte."
    )

    pdf.chapter_title("1", "Despliegue")
    pdf.body(
        "docker compose up -d --build. Tras desplegar, junto al nombre debe verse v0.22.5 y el worker "
        "se pedira como .../pdf.worker.min-*.js (nombre nuevo, sin cache vieja). Ctrl+F5 para recargar."
    )

    pdf.chapter_title("2", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.22.5)", "Fix definitivo: worker de PDF.js emitido como .js (rompe cache/MIME)."),
        ("Hecho (V-0.22.4)", "Version visible junto al nombre + fix despliegue/MIME del worker."),
        ("Hecho (V-0.22.3)", "Fix: worker de PDF.js servido como text/javascript en prod."),
        ("Hecho (V-0.22.2)", "Fix: pdf_url relativa en dev; endpoint /ficha/ en app principal."),
        ("Hecho (V-0.22.1)", "Visor PDF.js: la ficha PDF se ve en moviles."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.22.5.pdf")
    build_pdf(output)
