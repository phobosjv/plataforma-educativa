# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.21.3.pdf usando fpdf2."""
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

VERSION = "V-0.21.3"
FECHA = "2026-06-18"


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
            "Reorganizacion del panel: los enlaces de donacion, las redes sociales y la publicidad se "
            "mueven de 'Apariencia' a una pagina propia, 'Monetizacion y RRSS'. Cambio solo de interfaz; "
            "ambas paginas guardan por el mismo PUT /config/general partiendo de la config actual "
            "completa, asi una no pisa los ajustes de la otra. Sin cambios de backend ni de API.",
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
    pdf.chapter_title("0", "Seccion 'Monetizacion y RRSS'")
    pdf.section("Que cambia")
    pdf.bullet([
        "Donacion, redes sociales y publicidad se mueven de 'Apariencia' a una pagina propia: "
        "Monetizacion y RRSS (/admin/monetizacion).",
        "Apariencia se queda con nombre del sitio, logo, fuente, fondo, Aula Abierta y textos del catalogo.",
        "Solo interfaz: la funcionalidad es la misma, mejor organizada.",
    ])
    pdf.section("Como se evita pisar ajustes")
    pdf.bullet([
        "PUT /config/general reemplaza toda la config. Cada pagina parte de ajustesActuales (config "
        "actual completa) y solo sobrescribe SU seccion, asi guardar en una no borra los ajustes de la otra.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "Sin cambios de backend, API ni esquema. Type-check limpio + 9 E2E en verde (225 tests backend).",
    ])

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE I - MANUAL TECNICO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("1", "Cambios")
    pdf.kv_table([
        ("MonetizacionPage.tsx", "Nueva pagina: donacion, redes y publicidad"),
        ("ConfiguracionPage.tsx", "Apariencia pierde esas 3 secciones"),
        ("useConfig.ts", "Expone ajustesActuales (config actual como request)"),
        ("App.tsx + AdminLayout.tsx", "Ruta /admin/monetizacion + enlace de navegacion"),
    ])

    pdf.chapter_title("2", "Como se evita pisar ajustes")
    pdf.body(
        "El endpoint PUT /config/general reemplaza toda la configuracion. Para repartir los ajustes en "
        "dos paginas sin que una borre los de la otra, cada formulario parte de ajustesActuales (la "
        "configuracion actual completa) y solo sobrescribe su seccion antes de enviar. Sin cambios de "
        "API ni de backend."
    )

    pdf.chapter_title("3", "Tests")
    pdf.code(
        "cd backend && python -m pytest tests/unit tests/integration -q   # 225 (sin cambios)\n"
        "cd frontend && npm run test:e2e                                  # 9 E2E"
    )

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("4", "Donde esta cada cosa ahora (admin)")
    pdf.bullet([
        "Apariencia: nombre del sitio, logo, fuente, fondo/estampado, Aula Abierta y textos de la portada.",
        "Monetizacion y RRSS (nueva entrada del menu): botones de donacion, iconos de redes del pie y el "
        "codigo de publicidad de los margenes.",
        "La publicidad solo se ve en las pantallas de navegacion del catalogo, nunca durante un ejercicio.",
    ])

    pdf.chapter_title("5", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.21.3)", "Seccion 'Monetizacion y RRSS' separada de 'Apariencia'."),
        ("Hecho (V-0.21.2)", "Integridad referencial a nivel de BD."),
        ("Hecho (V-0.21.1)", "Correcciones del contador de visitas."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.21.3.pdf")
    build_pdf(output)
