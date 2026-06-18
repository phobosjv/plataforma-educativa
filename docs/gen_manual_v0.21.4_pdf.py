# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.21.4.pdf usando fpdf2."""
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

VERSION = "V-0.21.4"
FECHA = "2026-06-19"


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
            "Mejoras de usabilidad en la tabla de administracion de contenidos: nuevas columnas Ciclo, "
            "Curso y Asignatura; ordenacion al pulsar la cabecera de cada columna; y paginacion de 10 en "
            "10 con botones Primero/Anterior/Siguiente/Ultimo e indicador 'Pagina X de Y'. Cambio solo de "
            "interfaz: sin cambios de backend, API ni esquema.",
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
    pdf.chapter_title("0", "Tabla de contenidos: taxonomia, orden y paginacion")
    pdf.section("Que cambia")
    pdf.bullet([
        "Tres columnas nuevas en /admin/contenidos: Ciclo, Curso y Asignatura. Sin clasificar = '-'.",
        "Ordenacion al pulsar cualquier cabecera; segundo clic invierte el sentido (flecha arriba/abajo).",
        "Paginacion de 10 en 10 con botones Primero/Anterior/Siguiente/Ultimo e indicador 'Pagina X de Y'.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "Solo interfaz: sin cambios de backend, API ni esquema. Los nombres de taxonomia se resuelven "
        "en el frontend desde los IDs que ya devolvia la API.",
        "Type-check limpio; 225 tests backend y 9 E2E sin cambios. Verificado en navegador con Playwright.",
    ])

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE I - MANUAL TECNICO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("1", "Cambios")
    pdf.kv_table([
        ("ContenidosPage.tsx", "Columnas Ciclo/Curso/Asignatura, orden por columna, paginacion de 10."),
        ("tokens.css", "Estilos cms-th-sortable (flecha) y cms-pagination."),
    ])

    pdf.chapter_title("2", "Detalles de implementacion")
    pdf.body(
        "ContenidoResponse ya incluia ciclo_id, curso_id y asignatura_id; el frontend construye mapas "
        "id -> nombre con los endpoints de taxonomia (mismas queryKey que el catalogo, asi se sirven de la "
        "cache de React Query). No se ha tocado el contrato de la API. La ordenacion compara cadenas con "
        "localeCompare espanol (insensible a acentos/mayusculas) y las visitas numericamente; los valores "
        "vacios (sin clasificar) van al final. La paginacion es de cliente sobre la lista ordenada; cambiar "
        "el orden reinicia a la pagina 1 y la pagina actual se recorta si disminuye el total de filas."
    )

    pdf.chapter_title("3", "Tests")
    pdf.code(
        "cd backend && python -m pytest tests/unit tests/integration -q   # 225 (sin cambios)\n"
        "cd frontend && npx tsc --noEmit                                  # type-check limpio\n"
        "cd frontend && npm run test:e2e                                  # 9 E2E"
    )

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("4", "Usar la tabla de contenidos (admin/editor)")
    pdf.bullet([
        "Ademas de Titulo, Tipo, Estado y Visitas, la tabla muestra ahora Ciclo, Curso y Asignatura.",
        "Para ordenar, pulsa el titulo de una columna: flecha arriba = ascendente, otro clic = descendente.",
        "Con mas de 10 contenidos la lista se pagina. Botones: Primero, Anterior, Siguiente, Ultimo.",
        "El texto central indica la pagina actual y el total (p. ej. 'Pagina 2 de 5').",
    ])

    pdf.chapter_title("5", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.21.4)", "Tabla de contenidos: columnas de taxonomia, orden y paginacion."),
        ("Hecho (V-0.21.3)", "Seccion 'Monetizacion y RRSS' separada de 'Apariencia'."),
        ("Hecho (V-0.21.2)", "Integridad referencial a nivel de BD."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.21.4.pdf")
    build_pdf(output)
