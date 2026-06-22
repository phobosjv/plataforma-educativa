# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.22.6.pdf usando fpdf2."""
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

VERSION = "V-0.22.6"
FECHA = "2026-06-22"


class ManualPDF(FPDF):

    def header(self) -> None:
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*INDIGO)
        self.cell(0, 8, "Plataforma Educativa - Manual Tecnico y de Usuario  " + VERSION, align="L")
        self.set_text_color(*BLACK)
        self.ln(0)
        self.set_draw_color(*INDIGO)
        self.set_line_width(0.4)
        self.line(MARGIN, self.get_y() + 1, PAGE_W - MARGIN, self.get_y() + 1)
        self.ln(6)

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {{nb}} | {VERSION} - {FECHA}", align="C")

    def cover(self) -> None:
        self.add_page()
        self.set_fill_color(*INDIGO)
        self.rect(0, 0, PAGE_W, 80, "F")
        self.set_y(22)
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(*WHITE)
        self.cell(0, 12, "Plataforma Educativa", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 14)
        self.cell(0, 8, "Manual Tecnico y de Usuario", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, VERSION + "  |  " + FECHA, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*BLACK)
        self.ln(60)
        self.set_font("Helvetica", "", 10)
        self.set_x(MARGIN)
        self.multi_cell(INNER_W, 5.5,
            "Sistema CMS educativo para alojar ejercicios interactivos, articulos de texto y "
            "fichas PDF, dirigido a alumnado de infantil y primaria. Acceso publico sin cuentas "
            "de alumno. Roles admin y editor para la gestion de contenidos. Desplegado con Docker "
            "y Caddy (HTTPS automatico)."
        )

    def chapter_title(self, num: str, title: str) -> None:
        self.set_fill_color(*INDIGO_LIGHT)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*INDIGO)
        self.set_x(MARGIN)
        self.cell(INNER_W, 9, f"  {num}.  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*BLACK)
        self.ln(3)

    def section(self, title: str) -> None:
        self.set_font("Helvetica", "B", 10)
        self.set_x(MARGIN)
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")

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

    pdf.chapter_title("1", "Columna Ultima Modificacion en la tabla de contenidos")
    pdf.body(
        "La tabla de contenidos del panel admin (Contenidos) gana una nueva columna "
        "'Ultima modificacion' que muestra la fecha y hora de la ultima edicion de cada "
        "contenido. Este dato ya estaba disponible en la API (campo updated_at de "
        "ContenidoResponse), por lo que no ha sido necesario ningun cambio en el backend ni "
        "en la base de datos."
    )
    pdf.bullet([
        "El orden por defecto de la tabla pasa a ser 'Ultima modificacion' descendente "
        "(el contenido editado mas recientemente aparece arriba).",
        "La columna es ordenable haciendo clic en su cabecera, igual que el resto.",
        "Formato de fecha: DD/MM/AAAA, HH:MM (locale es-ES).",
        "Se muestra en gris claro y letra pequena para no competir con el titulo.",
    ])

    pdf.chapter_title("2", "Toggle mostrar/ocultar numero de version (backlog #11)")
    pdf.body(
        "El admin puede controlar si el badge de version (ej. 'v0.22.6') que aparece junto "
        "al nombre del sitio se muestra o se oculta. La opcion esta en Apariencia, como un "
        "checkbox 'Mostrar numero de version junto al nombre del sitio'."
    )
    pdf.bullet([
        "El flag mostrar_version (bool, default True) se almacena en site_config.",
        "Migracion Alembic 019: ADD COLUMN mostrar_version BOOLEAN NOT NULL DEFAULT TRUE.",
        "Se propaga por todas las capas: dominio, repo, DTO, command, handler, schema, router.",
        "El cliente OpenAPI se ha regenerado para incluir el nuevo campo.",
        "PublicLayout y AdminLayout renderizan el badge solo si mostrar_version es true.",
        "El valor por defecto (True) garantiza retrocompatibilidad con instalaciones existentes.",
    ])

    pdf.chapter_title("3", "Despliegue")
    pdf.body(
        "Actualizar con el comando habitual: docker compose up -d --build. "
        "La migracion 019 (ADD COLUMN mostrar_version) se aplica automaticamente en el "
        "entrypoint al arrancar. El badge de version debe mostrar v0.22.6 tras el despliegue."
    )

    pdf.chapter_title("4", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.22.6)", "Columna 'Ultima modificacion' + toggle mostrar/ocultar version."),
        ("Hecho (V-0.22.5)", "Fix definitivo: worker de PDF.js emitido como .js (rompe cache/MIME)."),
        ("Hecho (V-0.22.4)", "Version visible junto al nombre + fix despliegue/MIME del worker."),
        ("Hecho (V-0.22.3)", "Fix: worker de PDF.js servido como text/javascript en prod."),
        ("Hecho (V-0.22.2)", "Fix: pdf_url relativa en dev; endpoint /ficha/ en app principal."),
        ("Hecho (V-0.22.1)", "Visor PDF.js: la ficha PDF se ve en moviles."),
        ("Hecho (V-0.22.0)", "Tercer tipo de contenido: ficha PDF imprimible."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.22.6.pdf")
    build_pdf(output)
