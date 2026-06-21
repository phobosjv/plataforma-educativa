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

VERSION = "V-0.22.2"
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
            "Arreglo de CONFIGURACION: el visor PDF no cargaba en dev ni desde movil en red local. "
            "La pdf_url apuntaba al sandbox en localhost:8002 (no arrancado en dev; inaccesible "
            "desde movil). Ahora PDF_BASE_URL vacia produce una URL relativa (/ficha/<hash>.pdf) "
            "que Vite proxea al backend principal. En produccion Docker-Compose fija PDF_BASE_URL "
            "al subdominio sandbox, sin cambio de comportamiento.",
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

    pdf.chapter_title("0", "El visor PDF ya funciona en dev y movil LAN")
    pdf.section("Problema")
    pdf.body(
        "La pdf_url apuntaba a http://localhost:8002/ficha/<hash>.pdf (el servidor sandbox). "
        "En dev ese servidor normalmente no esta arrancado, y desde un movil en red local "
        "localhost apunta al propio movil (no al PC). PDF.js fallaba con error de red y "
        "mostraba el mensaje de fallback."
    )
    pdf.section("Solucion: PDF_BASE_URL vacia en dev")
    pdf.bullet([
        "Nueva variable de entorno PDF_BASE_URL (vacia por defecto en dev).",
        "URL relativa /ficha/<hash>.pdf en dev: Vite la proxea al backend principal.",
        "Nuevo endpoint GET /ficha/{hash}.pdf en la app principal: sirve el fichero desde media/ "
        "con Content-Disposition, Cache-Control immutable y Access-Control-Allow-Origin: *.",
        "En produccion, docker-compose fija PDF_BASE_URL=https://${SANDBOX_DOMAIN}: la URL "
        "sigue siendo absoluta al subdominio sandbox. Sin cambio de comportamiento en prod.",
        "console.error en PdfViewer.tsx para facilitar la depuracion futura.",
    ])

    pdf.chapter_title("1", "Despliegue")
    pdf.body(
        "Sin migracion ni reconstruccion del frontend. En produccion basta con "
        "docker compose up -d --build para que el api recoja PDF_BASE_URL del compose."
    )

    pdf.chapter_title("2", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.22.2)", "Fix: pdf_url relativa en dev; endpoint /ficha/ en app principal."),
        ("Hecho (V-0.22.1)", "Visor PDF.js: la ficha PDF se ve en moviles."),
        ("Hecho (V-0.22.0)", "Tercer tipo de contenido: ficha PDF imprimible."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.22.2.pdf")
    build_pdf(output)
