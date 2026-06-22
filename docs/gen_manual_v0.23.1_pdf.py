# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.23.1.pdf usando fpdf2."""
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

VERSION = "V-0.23.1"
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
            "y Caddy (HTTPS automatico). Instalable como PWA en moviles y tablets."
        )

    def chapter_title(self, num: str, title: str) -> None:
        self.set_fill_color(*INDIGO_LIGHT)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*INDIGO)
        self.set_x(MARGIN)
        self.cell(INNER_W, 9, f"  {num}.  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*BLACK)
        self.ln(3)

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

    pdf.chapter_title("1", "Icono de la PWA: corregido y derivado del logo")
    pdf.body(
        "En V-0.23.0 el icono de la app instalada aparecia como una circunferencia en blanco. "
        "La causa: el generador de iconos placeholder creaba la imagen en modo RGB pero pintaba "
        "el circulo con un color semitransparente; al ignorarse el canal alfa en RGB, salia un "
        "circulo blanco solido con el texto (tambien blanco) invisible encima. Ademas, al estar "
        "marcado como 'maskable', el sistema operativo lo recortaba a un circulo."
    )
    pdf.body(
        "Ahora los iconos se generan dinamicamente en el backend a partir de la configuracion del "
        "sitio, honrando la decision del usuario:"
    )
    pdf.bullet([
        "Si hay un LOGO subido en Administracion (Apariencia), se usa como icono de la app, "
        "centrado sobre una baldosa blanca.",
        "Si NO hay logo, se genera un icono generico con las iniciales del nombre del sitio "
        "sobre el color primario de la paleta activa.",
        "Cuatro variantes: 192x192 y 512x512, cada una con proposito 'any' (a sangre) y "
        "'maskable' (con zona segura para el recorte del sistema operativo).",
        "Nuevo endpoint publico GET /icons/{nombre}.png. El manifiesto enlaza las cuatro "
        "variantes con sus 'purpose' y 'sizes' correctos.",
        "Se sirve sin cache: cambiar el logo o la paleta se refleja en la siguiente instalacion.",
        "Nueva dependencia de backend: Pillow (procesado de imagen).",
    ])

    pdf.chapter_title("2", "Importante: reinstalar para ver el icono nuevo")
    pdf.body(
        "Las apps PWA ya instaladas CACHEAN el icono en el dispositivo. Tras desplegar esta "
        "version, hay que DESINSTALAR la app del telefono/ordenador y volver a instalarla (Anadir "
        "a pantalla de inicio / Instalar aplicacion) para que tome el icono nuevo. En el navegador "
        "puede ayudar recargar sin cache la primera vez."
    )

    pdf.chapter_title("3", "Despliegue")
    pdf.body(
        "Actualizar con: docker compose up -d --build. El --build es necesario porque se anade "
        "una dependencia nueva (Pillow) al backend y cambian los ficheros del frontend. No hay "
        "migracion de base de datos. Tras el despliegue, el badge de version debe mostrar v0.23.1."
    )

    pdf.chapter_title("4", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.23.1)", "Fix icono PWA (circulo blanco) + iconos derivados del logo."),
        ("Hecho (V-0.23.0)", "PWA instalable: manifiesto dinamico, service worker, iconos."),
        ("Hecho (V-0.22.6)", "Columna 'Ultima modificacion' + toggle mostrar/ocultar version."),
        ("Hecho (V-0.22.0)", "Tercer tipo de contenido: ficha PDF imprimible."),
        ("Pendiente", "Cache offline (lectura de articulos sin conexion) - V-0.24.0+."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.23.1.pdf")
    build_pdf(output)
