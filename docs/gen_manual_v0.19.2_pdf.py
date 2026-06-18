# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.19.2.pdf usando fpdf2."""
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

VERSION = "V-0.19.2"
FECHA = "2026-06-17"


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
            "Mejoras de visibilidad (UI): el pie de la web publica (apoyo/donaciones, lema y redes) queda "
            "SIEMPRE visible sin hacer scroll; y en el panel, los botones 'Ver la web' y 'Cerrar sesion' "
            "estan siempre a la vista al fondo de la barra lateral fija. Cambio solo de CSS, sin tocar "
            "componentes, API ni esquema.",
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

    def code(self, text: str) -> None:
        self.set_fill_color(*GRAY_BG)
        self.set_font("Courier", "", 8)
        self.set_x(MARGIN)
        self.multi_cell(INNER_W, 5, text, border="1", fill=True)
        self.set_font("Helvetica", "", 10)
        self.ln(2)

    def kv_table(self, rows: list) -> None:
        col1 = 60
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

    # ---- NOVEDADES ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 10, "NOVEDADES DE " + VERSION, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)
    pdf.chapter_title("0", "Mejoras de visibilidad (UI)")
    pdf.section("Que cambia")
    pdf.bullet([
        "Pie de la web publica SIEMPRE visible sin scroll: apoyo/donaciones, lema y los iconos de redes "
        "quedan anclados al fondo del viewport mientras se navega; al final del documento ocupan su "
        "sitio natural y NO tapan el contenido. Fondo opaco.",
        "Acciones de admin/editor SIEMPRE visibles: la barra lateral del panel queda fija a la altura "
        "del viewport, con 'Ver la web' y 'Cerrar sesion' siempre accesibles al fondo.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "Cambio SOLO de CSS (tokens.css), sin tocar componentes, API ni esquema. NO hay migracion.",
        "205 tests backend + 9 E2E en verde. Type-check frontend limpio.",
    ])

    # ---- PARTE I: MANUAL TECNICO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE I - MANUAL TECNICO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("1", "Ficheros afectados")
    pdf.kv_table([
        (".cms-footer", "position: sticky; bottom:0 + fondo opaco + z-index 50"),
        (".cms-sidebar", "position: sticky; top:0; height:100vh; overflow-y:auto"),
    ])

    pdf.chapter_title("2", "Notas de diseno")
    pdf.body(
        "El pie usa position: sticky (no fixed): permanece anclado al fondo del viewport mientras hay "
        "contenido por debajo y, al final, ocupa su espacio natural, de modo que NO oculta el ultimo "
        "contenido. Capas (z-index): navegacion 100, pie 50, rieles de publicidad 5, ejercicio "
        "maximizado 1000 (el pie nunca asoma sobre un ejercicio a pantalla completa). La barra lateral "
        "del panel es sticky a 100vh con overflow-y:auto: con el numero habitual de secciones todo cabe "
        "y las acciones quedan ancladas abajo; si creciera, la propia barra scrollea."
    )

    pdf.chapter_title("3", "Tests")
    pdf.code(
        "cd backend && python -m pytest tests/unit tests/integration -q   # 205\n"
        "cd frontend && npm run test:e2e                                  # 9 E2E"
    )

    # ---- PARTE II: MANUAL DE USUARIO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("4", "Para visitantes")
    pdf.body(
        "El pie con las opciones de apoyo al proyecto y las redes sociales se ve siempre, sin tener que "
        "desplazarse hasta el final de la pagina."
    )

    pdf.chapter_title("5", "Para administradores y editores")
    pdf.body(
        "En el panel, los botones 'Ver la web' y 'Cerrar sesion' estan siempre a la vista en la parte "
        "inferior de la barra lateral, aunque la pagina de trabajo sea larga."
    )

    pdf.chapter_title("6", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.19.2)", "Pie publico y acciones de admin/editor siempre visibles."),
        ("Hecho (V-0.19.1)", "Backend sin privilegios (usuario no-root) en Docker."),
        ("Hecho (V-0.19.0)", "Iconos de red en articulos + autor de cada version."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.19.2.pdf")
    build_pdf(output)
