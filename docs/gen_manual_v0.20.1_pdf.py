# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.20.1.pdf usando fpdf2."""
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

VERSION = "V-0.20.1"
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
            "Release de correccion (auditoria de logica): (1) borrar taxonomia con dependencias se "
            "bloquea (409) para no dejar contenido huerfano fuera del catalogo; (2) no se puede publicar "
            "un ejercicio interactivo sin su fichero HTML; (3) importar ya no arrastra las visitas del "
            "sitio anterior. Sin cambios de esquema ni de contrato.",
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
    pdf.cell(0, 10, "CORRECCIONES DE " + VERSION, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)
    pdf.chapter_title("0", "Hallazgos de la auditoria de logica")
    pdf.section("Integridad referencial al borrar taxonomia")
    pdf.bullet([
        "SQLite no fuerza las claves foraneas: borrar un ciclo con cursos, o un curso/asignatura "
        "referenciado por contenidos, dejaba referencias colgando y el contenido desaparecia "
        "silenciosamente del catalogo.",
        "Ahora el borrado se bloquea con 409 Conflict y mensaje claro (cuenta tambien la papelera). La "
        "pagina de Taxonomia muestra el motivo (antes el borrado fallido no daba ninguna pista).",
    ])
    pdf.section("Publicar ejercicio interactivo")
    pdf.bullet([
        "No se puede publicar un interactivo sin su fichero HTML (antes mostraba una pagina vacia en "
        "publico). publicar() lo rechaza con un mensaje claro.",
    ])
    pdf.section("Importacion y visitas")
    pdf.bullet([
        "Tras importar, el contador de visitas en memoria (IDs del sitio anterior) se descarta, para no "
        "volcarlo como filas huerfanas en el sitio recien importado.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "Sin cambios de esquema ni de contrato (los modelos de respuesta no cambian).",
        "216 tests backend (6 nuevos) + 9 E2E en verde. Type-check frontend limpio.",
    ])

    # ---- PARTE I: MANUAL TECNICO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE I - MANUAL TECNICO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("1", "Cambios")
    pdf.kv_table([
        ("taxonomy (dominio)", "Puerto ContenidoEnTaxonomia; handlers Eliminar* comprueban dependencias"),
        ("content (infra)", "Adapter SqlAlchemyContenidoEnTaxonomia (cuenta por curso/asignatura)"),
        ("taxonomy (API)", "Los borrados devuelven 409 Conflict con el motivo"),
        ("content (dominio)", "publicar() exige hash_html en los interactivos"),
        ("maintenance (API)", "La importacion vacia el buffer de visitas tras importar"),
        ("frontend TaxonomiaPage", "Las acciones de borrado muestran el error del backend"),
    ])

    pdf.chapter_title("2", "Regla de dependencia")
    pdf.body(
        "El puerto ContenidoEnTaxonomia se declara en el dominio de taxonomy; su implementacion vive en "
        "la infraestructura de content y se inyecta en el router (capa de composicion). Asi taxonomy NO "
        "importa content: la dependencia apunta hacia adentro, como exige la arquitectura hexagonal."
    )

    pdf.chapter_title("3", "Tests")
    pdf.code(
        "cd backend && python -m pytest tests/unit tests/integration -q   # 216 (6 nuevos)\n"
        "cd frontend && npm run test:e2e                                  # 9 E2E"
    )
    pdf.body(
        "Nuevos: borrar ciclo con cursos / curso con contenido / asignatura con contenido (409) y "
        "borrado limpio (204); publicar interactivo sin HTML (400); el buffer de visitas se vacia tras "
        "importar."
    )

    # ---- PARTE II: MANUAL DE USUARIO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("4", "Borrado de taxonomia")
    pdf.body(
        "Si intentas borrar un ciclo, curso o asignatura que todavia tiene elementos asociados (cursos o "
        "contenidos), el panel te avisara y NO lo borrara, para no dejar contenido 'huerfano' fuera de "
        "la navegacion. Reasigna o elimina primero esos elementos."
    )

    pdf.chapter_title("5", "Publicar ejercicios")
    pdf.body(
        "Un ejercicio interactivo solo puede publicarse DESPUES de subir su fichero HTML. Si lo intentas "
        "antes, veras un aviso."
    )

    pdf.chapter_title("6", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.20.1)", "Correcciones: taxonomia, publicar interactivo, buffer de visitas."),
        ("Hecho (V-0.20.0)", "Importar / restaurar el sitio (BD + media)."),
        ("Hecho (V-0.19.1)", "Backend sin privilegios (no-root) en Docker."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.20.1.pdf")
    build_pdf(output)
