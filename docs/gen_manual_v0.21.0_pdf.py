# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.21.0.pdf usando fpdf2."""
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

VERSION = "V-0.21.0"
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
            "Ejercicios tipo 'Examen': los ejercicios interactivos pueden marcarse como simulacro de "
            "examen. En el catalogo se muestran AL FINAL de cada lista y con un icono distinto. La "
            "fusion de varios ejercicios la hace a mano el disenador; la app solo aporta la marca, el "
            "orden y el icono. Solo aplica a interactivos (no a textos). Migracion 016 (is_exam).",
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
        col1 = 64
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
    pdf.chapter_title("0", "Ejercicios tipo 'Examen'")
    pdf.section("Que hace")
    pdf.bullet([
        "Al crear/editar un contenido INTERACTIVO aparece un check 'Examen'. No aplica a textos (el "
        "dominio rechaza marcar un texto como examen).",
        "En el catalogo, los examenes se muestran AL FINAL de cada lista (ciclo/curso/asignatura, Aula "
        "Abierta y 'Ver todo') y con un icono/badge distinto.",
        "Suelen ser ejercicios mas largos (fusion de varios); esa combinacion la hace a mano el "
        "disenador. La app solo aporta la marca, el orden y el icono.",
    ])
    pdf.section("Persistencia")
    pdf.bullet([
        "content gana la columna is_exam (Boolean, default false). Migracion Alembic 016.",
        "Cliente OpenAPI regenerado: campo es_examen en ContenidoResponse y en crear/actualizar.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "219 tests backend (3 nuevos) + 9 E2E en verde. Type-check frontend limpio. API -> 0.21.0.",
    ])

    # ---- PARTE I: MANUAL TECNICO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE I - MANUAL TECNICO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("1", "API")
    pdf.kv_table([
        ("POST /contenidos/", "Acepta es_examen (bool); solo valido en tipo interactivo"),
        ("PUT /contenidos/{id}", "Acepta es_examen (bool opcional) para marcar/desmarcar"),
        ("GET /contenidos/...", "ContenidoResponse incluye es_examen"),
    ])
    pdf.body(
        "Marcar como examen un contenido de tipo texto responde 400 (regla de dominio: solo un "
        "ejercicio interactivo puede marcarse como examen)."
    )

    pdf.chapter_title("2", "Modelo de datos")
    pdf.body(
        "content gana is_exam (Boolean, default false). Migracion 016. El campo de dominio es "
        "Contenido.es_examen; la invariante (solo interactivo) se valida en el agregado (__post_init__ "
        "y marcar_examen)."
    )

    pdf.chapter_title("3", "Catalogo (frontend)")
    pdf.body(
        "CatalogoPage ordena cada lista con examenesAlFinal() (orden estable: los examenes al final, "
        "conservando el orden del resto) y la tarjeta muestra un badge cms-badge-examen con el icono. "
        "La busqueda NO se reordena (manda la relevancia)."
    )

    pdf.chapter_title("4", "Instalacion / despliegue")
    pdf.code(
        "cd plataforma-educativa\n"
        "docker compose up -d --build\n"
        "# El entrypoint corre alembic upgrade head: la migracion 016 anade is_exam (default false)."
    )

    pdf.chapter_title("5", "Tests")
    pdf.code(
        "cd backend && python -m pytest tests/unit tests/integration -q   # 219 (3 nuevos)\n"
        "cd frontend && npm run test:e2e                                  # 9 E2E"
    )

    # ---- PARTE II: MANUAL DE USUARIO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("6", "Marcar un ejercicio como examen (editor/admin)")
    pdf.bullet([
        "Crea o edita un contenido de tipo 'Ejercicio interactivo (HTML)'.",
        "Marca el check 'Examen'.",
        "Sube el fichero HTML del examen (puede ser la fusion de varios ejercicios que prepares aparte) "
        "y publicalo.",
        "En el catalogo, el examen aparecera AL FINAL de su lista, con un distintivo que lo diferencia.",
    ])

    pdf.chapter_title("7", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.21.0)", "Ejercicios tipo 'Examen' (marca + orden al final + icono)."),
        ("Hecho (V-0.20.1)", "Correcciones de auditoria (taxonomia, publicar, buffer de visitas)."),
        ("Hecho (V-0.20.0)", "Importar / restaurar el sitio (BD + media)."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.21.0.pdf")
    build_pdf(output)
