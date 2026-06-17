# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.19.1.pdf usando fpdf2."""
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

VERSION = "V-0.19.1"
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
            "Endurecimiento de seguridad: el contenedor del backend ya NO ejecuta la aplicacion como "
            "root. Se crea un usuario sin privilegios (appuser) y, mediante gosu, el entrypoint baja "
            "privilegios tras ajustar los permisos de los volumenes. Principio de menor privilegio: "
            "reduce el daño ante una eventual RCE. Cambio solo de infraestructura (Dockerfile + "
            "entrypoint), sin tocar codigo, API ni esquema.",
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
    pdf.chapter_title("0", "Backend sin privilegios (usuario no-root)")
    pdf.section("Que cambia")
    pdf.bullet([
        "El contenedor del backend ya NO ejecuta la aplicacion como root. Principio de menor privilegio: "
        "si apareciera una RCE, el proceso comprometido no seria root dentro del contenedor (dificulta "
        "escalar y escapar).",
        "Dockerfile: instala gosu y crea el usuario appuser (UID/GID 10001, configurables con los "
        "build-args APP_UID/APP_GID).",
        "entrypoint.sh: arranca como root SOLO para hacer chown de los bind mounts (/app/data y "
        "/app/media) y luego se reinvoca con 'gosu appuser'. Migraciones, seed y uvicorn corren ya sin "
        "privilegios (patron de la imagen oficial de postgres).",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "Cambio SOLO de infraestructura (Dockerfile + entrypoint + docs); sin cambios de codigo, API ni "
        "esquema. NO hay migracion nueva. 205 tests backend en verde.",
        "REQUIERE validar en el servidor (Docker no esta en el entorno de desarrollo).",
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
        ("backend/Dockerfile", "Instala gosu; crea appuser (ARG APP_UID/APP_GID); chown data/media"),
        ("backend/entrypoint.sh", "Arranca root, chown de bind mounts y baja a appuser con gosu"),
        ("docs/seguridad-imagenes.md", "Documenta el setup no-root y la validacion en el servidor"),
    ])

    pdf.chapter_title("2", "Despliegue")
    pdf.code(
        "cd plataforma-educativa\n"
        "docker compose up -d --build\n"
        "# alembic upgrade head corre ya como appuser. Esta version NO anade migraciones.\n"
        "# Alinear con un UID/GID del host:\n"
        "docker compose build --build-arg APP_UID=<uid> --build-arg APP_GID=<gid> api"
    )

    pdf.chapter_title("3", "Validacion en el servidor")
    pdf.code(
        "# 1) uvicorn corre como appuser (no root):\n"
        "docker compose exec api ps -o user,pid,comm\n"
        "# 2) sin errores de permisos; migraciones y seed correctos:\n"
        "docker compose logs api | grep -i -E \"permission|denied|alembic|admin\""
    )
    pdf.body(
        "Si los bind mounts tenian ficheros de propietario root de versiones anteriores, el chown del "
        "entrypoint los reasigna a appuser en el primer arranque (coste unico; puede tardar algo si "
        "./media tiene muchos ficheros)."
    )

    pdf.chapter_title("4", "Seguridad")
    pdf.bullet([
        "El healthcheck del compose se ejecuta via docker exec (root); solo hace un urlopen a "
        "localhost:8000/health, no requiere privilegios y sigue funcionando.",
        "Aislamiento del sandbox, sanitizacion asimetrica del HTML de articulos y tratamiento de datos "
        "de menores: sin cambios.",
    ])

    pdf.chapter_title("5", "Tests")
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

    pdf.chapter_title("6", "Sin cambios visibles")
    pdf.body(
        "Esta version no introduce cambios visibles para administradores, editores ni visitantes: es "
        "una mejora interna de seguridad del despliegue."
    )

    pdf.chapter_title("7", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.19.1)", "Backend sin privilegios (usuario no-root con gosu) en Docker."),
        ("Hecho (V-0.19.0)", "Iconos de red en articulos + autor de cada version."),
        ("Pendiente (UI)", "Pie de la web siempre visible; acciones admin/editor siempre visibles."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.19.1.pdf")
    build_pdf(output)
