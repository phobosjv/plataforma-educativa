# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.17.0.pdf usando fpdf2."""
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

VERSION = "V-0.17.0"
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
            "Este documento describe la arquitectura, endpoints de la API, modelo de datos, "
            "guia de instalacion y manual de uso de la Plataforma Educativa " + VERSION + ". "
            "Esta version anade el HISTORIAL DE VERSIONES y la RESTAURACION de contenidos: en la "
            "edicion se ven las versiones guardadas y se puede volver a un estado anterior. Restaurar "
            "no destruye historial (crea una version nueva), por lo que es reversible.",
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
        col1 = 65
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

    def endpoint_table(self, rows: list) -> None:
        cols = [18, 90, 22, INNER_W - 18 - 90 - 22]
        headers = ["Metodo", "Ruta", "Auth", "Descripcion"]
        self.set_fill_color(*INDIGO)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 8)
        self.set_x(MARGIN)
        for h, w in zip(headers, cols):
            self.cell(w, 6, " " + h, border=1, fill=True)
        self.ln()
        self.set_text_color(*BLACK)
        for i, (method, path, auth, desc) in enumerate(rows):
            fill = i % 2 == 0
            self.set_fill_color(245, 247, 250) if fill else self.set_fill_color(255, 255, 255)
            self.set_x(MARGIN)
            self.set_font("Courier", "B", 8)
            self.cell(cols[0], 5.5, " " + method, border=1, fill=fill)
            self.set_font("Courier", "", 7)
            self.cell(cols[1], 5.5, " " + path, border=1, fill=fill)
            self.set_font("Helvetica", "", 8)
            self.cell(cols[2], 5.5, " " + auth, border=1, fill=fill)
            self.multi_cell(cols[3], 5.5, " " + desc, border=1, fill=fill)
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
    pdf.chapter_title("0", "Cambios de esta version")
    pdf.section("Anadido: historial de versiones y restauracion")
    pdf.bullet([
        "Historial de versiones en la edicion de un contenido: numero, titulo y fecha; la mas reciente "
        "marcada como 'actual'.",
        "Restaurar una version anterior: devuelve el contenido a ese estado (titulo, descripcion, "
        "etiquetas, cuerpo HTML o ejercicio).",
        "Restaurar NO destruye historial: crea una version nueva con el estado restaurado (CLAUDE.md "
        "7), por lo que es reversible.",
        "Endpoints GET /contenidos/{id}/versiones y POST /contenidos/{id}/versiones/{n}/restaurar "
        "(editor+). La restauracion se registra en la auditoria.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "Sin cambios de esquema: content_version ya existia y cada modificacion crea una version inmutable.",
        "196 tests backend (4 nuevos) + 9 E2E en verde. Type-check de frontend limpio. API -> 0.17.0.",
    ])

    # ---- PARTE I: MANUAL TECNICO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE I - MANUAL TECNICO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("1", "Descripcion del sistema")
    pdf.body(
        "Plataforma web educativa tipo CMS para alojar y ejecutar ejercicios interactivos "
        "(HTML/CSS/JS autocontenidos) y articulos de texto, para infantil y primaria. Acceso publico "
        "sin cuentas de alumno. Dos roles: admin y editor."
    )
    pdf.section("Caracteristicas principales")
    pdf.bullet([
        "Catalogo navegable + buscador full-text; contador de visitas anonimas.",
        "Nombre, logotipo, paleta, textos de portada, donaciones y publicidad configurables.",
        "Auditoria de acciones de gestion y versionado con restauracion de contenidos.",
        "Ejercicios en iframe aislado con sandbox; articulos con HTML saneado en servidor.",
    ])

    pdf.chapter_title("2", "Arquitectura del backend")
    pdf.section("Contextos acotados implementados")
    pdf.kv_table([
        ("identity", "Usuarios, login JWT, guardas de rol"),
        ("content", "CRUD, VERSIONADO + RESTAURACION, papelera, articulos + ejercicios, FTS5"),
        ("taxonomy", "Ciclos, cursos y asignaturas (transversal -> Aula Abierta)"),
        ("configuration", "Sitio: nombre, fuente, fondo, logo, paletas, textos, donaciones, publicidad"),
        ("media", "Subida de imagenes (articulos y logo)"),
        ("analytics", "Contador de visitas"),
        ("auditing", "Registro de acciones de gestion"),
    ])
    pdf.section("Versionado (CLAUDE.md 7)")
    pdf.body(
        "Cada modificacion de un contenido (crear, editar, subir HTML, restaurar) anade una version "
        "INMUTABLE a content_version con un snapshot (titulo, descripcion, tipo, idioma, etiquetas) y "
        "el body_html/hash_html. Restaurar aplica el snapshot de una version al contenido y CREA UNA "
        "VERSION NUEVA: el historial nunca se destruye y la operacion es reversible."
    )

    pdf.chapter_title("3", "Instalacion y despliegue")
    pdf.section("Arranque rapido con Docker (Caddy + HTTPS)")
    pdf.code(
        "cd plataforma-educativa\n"
        "cp .env.example .env   # APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY, admin\n"
        "docker compose up -d --build\n"
        "# El entrypoint corre alembic upgrade head. Esta version NO anade migraciones."
    )
    pdf.section("Arranque en desarrollo local")
    pdf.code(
        "cd backend && python -m alembic upgrade head\n"
        "uvicorn app.main:app --reload --port 8001\n\n"
        "cd frontend && npm install && npm run dev   # http://localhost:5173"
    )

    pdf.chapter_title("4", "API - Versiones de contenido")
    pdf.endpoint_table([
        ("GET", "/contenidos/{id}/versiones", "editor+", "Historial (nº, titulo, tipo, autor, fecha)"),
        ("POST", "/contenidos/{id}/versiones/{n}/restaurar", "editor+", "Restaura a esa version (crea version nueva)"),
    ])
    pdf.body(
        "El resto de endpoints (contenidos + /buscar, /analytics/visitas, /auditoria, /config/*, "
        "/media/imagenes, /taxonomy/*, /admin/backups + /admin/export, sandbox) se mantienen como en V-0.16.0."
    )

    pdf.chapter_title("5", "Seguridad y privacidad")
    pdf.bullet([
        "Sandbox/sanitizacion: sin cambios (ejercicios aislados; HTML de articulos saneado).",
        "Versionado: versiones inmutables; restaurar nunca borra historial. Solo editor/admin ven y "
        "restauran versiones; la accion se audita.",
        "Menores: sin cuentas de alumno, sin cookies de seguimiento, visitas anonimas, sin perfilado.",
    ])

    pdf.chapter_title("6", "Tests")
    pdf.kv_table([
        ("Backend", "196 tests (unit + integracion)"),
        ("Versionado (V-0.17.0)", "listar, restaurar (revierte + crea version nueva), inexistente 404, guarda rol"),
        ("E2E (Playwright)", "9 flujos, incl. buscar y seguridad del sandbox"),
    ])
    pdf.code(
        "cd backend && python -m pytest tests/unit tests/integration -q   # 196\n"
        "cd frontend && npm run test:e2e                                  # 9 E2E"
    )

    # ---- PARTE II: MANUAL DE USUARIO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("7", "Historial de versiones y restauracion (novedad)")
    pdf.body("Al EDITAR un contenido en el panel, al final de la pagina aparece 'Historial de versiones':")
    pdf.bullet([
        "Muestra cada version guardada (numero, titulo y fecha). La mas reciente esta marcada como 'actual'.",
        "Para volver a un estado anterior, pulsa 'Restaurar' en la version deseada.",
        "El contenido recupera el titulo, descripcion, etiquetas y cuerpo (o ejercicio) de esa version.",
        "No se pierde nada: se crea una version nueva con el estado restaurado, asi que puedes deshacerlo.",
        "Cada crear/editar/subir HTML/restaurar guarda una version. La restauracion se registra en Auditoria.",
    ])

    pdf.chapter_title("8", "Resto del panel")
    pdf.body(
        "Sin cambios respecto a V-0.16.0 (Contenidos, Taxonomia, Usuarios, Copias, Auditoria, "
        "Apariencia con logo/fuente/fondo/paletas/textos/donaciones/publicidad)."
    )

    pdf.chapter_title("9", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.17.0)", "Historial de versiones y restauracion de contenidos."),
        ("Hecho (V-0.16.0)", "Donaciones, publicidad y textos del catalogo configurables."),
        ("Mas adelante", "Usuario no-root en el backend; mostrar autor de cada version; comparar versiones."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.17.0.pdf")
    build_pdf(output)
