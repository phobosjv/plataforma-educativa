# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.21.2.pdf usando fpdf2."""
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

VERSION = "V-0.21.2"
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
            "Integridad referencial a nivel de BD: SQLite hace cumplir ahora las claves foraneas "
            "(PRAGMA foreign_keys=ON) y content gana FK a la taxonomia (ON DELETE RESTRICT), una segunda "
            "capa sobre las guardas de dominio. Migracion 017 (recrea content; el indice FTS se suelta y "
            "reconstruye alrededor). Sin cambios de API.",
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

    # ---- NOVEDADES ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 10, "NOVEDADES DE " + VERSION, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)
    pdf.chapter_title("0", "Integridad referencial a nivel de BD")
    pdf.section("Que cambia")
    pdf.bullet([
        "Cada conexion activa PRAGMA foreign_keys=ON (antes solo WAL): se aplican las FK ya declaradas "
        "(curso.ciclo_id -> ciclo, content_version.content_id -> content).",
        "content gana FK a la taxonomia (ciclo_id/curso_id/asignatura_id) con ON DELETE RESTRICT: la BD "
        "rechaza que un contenido apunte a una taxonomia inexistente. Migracion 017.",
        "Es una segunda capa, a nivel de motor, sobre las guardas de dominio ya existentes.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "La purga de contenido sigue borrando sus versiones por la cascada del ORM. Sin cambios de API.",
        "225 tests backend (3 nuevos con FK activas) + 9 E2E en verde. Migracion 017 validada en dev.",
    ])

    # ---- PARTE I ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE I - MANUAL TECNICO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("1", "Cambios")
    pdf.kv_table([
        ("database.py", "El listener de conexion anade PRAGMA foreign_keys=ON"),
        ("content (ORM)", "ciclo_id/curso_id/asignatura_id con ForeignKey(ondelete=RESTRICT)"),
        ("Migracion 017", "Recrea content (batch SQLite); suelta y reconstruye el indice FTS"),
    ])

    pdf.chapter_title("2", "Por que se recrea content y el indice FTS")
    pdf.body(
        "SQLite no permite anadir una FK con ALTER: hay que recrear la tabla (batch de Alembic, que "
        "copia los datos). El indice content_fts es de contenido externo sobre content y mapea por "
        "rowid (cambia al recrear), por lo que la migracion lo suelta antes y lo reconstruye despues "
        "(rebuild), dejando la busqueda operativa. La migracion corre con las FK desactivadas (modo por "
        "defecto de Alembic), asi que la recreacion no tropieza con las referencias existentes."
    )

    pdf.chapter_title("3", "Despliegue")
    pdf.code(
        "cd plataforma-educativa\n"
        "docker compose up -d --build\n"
        "# El entrypoint corre alembic upgrade head: la migracion 017 anade las FK y reconstruye el indice."
    )
    pdf.body(
        "Si una instalacion tuviera referencias huerfanas previas, conviene revisarlas antes (en dev se "
        "verifico que no habia ninguna). Recomendado: copia o exportacion completa antes de actualizar."
    )

    pdf.chapter_title("4", "Tests")
    pdf.code(
        "cd backend && python -m pytest tests/unit tests/integration -q   # 225 (3 nuevos)\n"
        "cd frontend && npm run test:e2e                                  # 9 E2E"
    )

    # ---- PARTE II ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("5", "Sin cambios visibles")
    pdf.body(
        "Es una mejora interna de robustez. El comportamiento al borrar taxonomia es el mismo que ya "
        "introdujo V-0.20.1 (la app avisa y no borra si hay elementos asociados); ahora ademas la propia "
        "base de datos lo garantiza."
    )

    pdf.chapter_title("6", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.21.2)", "Integridad referencial a nivel de BD (FK activas + FK de content)."),
        ("Hecho (V-0.21.1)", "Correcciones del contador de visitas."),
        ("Hecho (V-0.21.0)", "Ejercicios tipo 'Examen'."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.21.2.pdf")
    build_pdf(output)
