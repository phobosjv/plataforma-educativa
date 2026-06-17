# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.18.0.pdf usando fpdf2."""
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

VERSION = "V-0.18.0"
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
            "Esta version anade las REDES SOCIALES: el administrador configura enlaces a redes "
            "(Facebook, Instagram, X, YouTube, TikTok, WhatsApp, Telegram, LinkedIn) con sus iconos "
            "(SVG self-hosted) en el pie de la web publica; y los editores pueden enlazar perfiles de "
            "terceros en el cuerpo de los articulos, abriendo en pestaña nueva de forma segura.",
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
    pdf.chapter_title("0", "Cambios de esta version")
    pdf.section("Anadido: redes sociales")
    pdf.bullet([
        "Pie configurable (admin): lista de enlaces a redes (Facebook, Instagram, X, YouTube, TikTok, "
        "WhatsApp, Telegram, LinkedIn) con su icono (SVG self-hosted, sin CDN externo, §10). URL http(s)://; "
        "cada red una sola vez.",
        "Editores: los enlaces del cuerpo de los articulos abren en pestaña nueva (target=_blank + "
        "rel=noopener noreferrer); permite enlazar perfiles de terceros (autores citados) sin sacar al "
        "menor del sitio. El HTML se sigue saneando siempre (nh3 + DOMPurify).",
        "site_config gana redes_sociales_json; migracion Alembic 015. Se guarda por PUT /config/general.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "205 tests backend (4 nuevos de redes sociales) + 9 E2E en verde. Type-check frontend limpio.",
        "Iconos self-hosted en app/config/redesSociales.tsx, asociados por el id de la red. API -> 0.18.0.",
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
        "CMS educativo para infantil y primaria: ejercicios interactivos (sandbox) y articulos de "
        "texto. Acceso publico sin cuentas de alumno. Roles admin y editor. Arquitectura hexagonal."
    )
    pdf.section("Funcionalidad principal")
    pdf.bullet([
        "Catalogo navegable + buscador; contador de visitas; auditoria; versionado con restauracion.",
        "Configuracion del sitio: nombre, logo, paleta, fondo, textos, donaciones, redes sociales, publicidad.",
        "Monetizacion ligera: donaciones + publicidad solo en zonas de adultos (§10).",
    ])

    pdf.chapter_title("2", "API - Configuracion (/config/)")
    pdf.kv_table([
        ("GET /config/", "Config del sitio (incluye redes_sociales)"),
        ("PUT /config/general (admin)", "Actualiza todos los ajustes del sitio"),
    ])
    pdf.body(
        "Campo nuevo de GET /config/: redes_sociales = lista de {red, url}. Redes soportadas: facebook, "
        "instagram, x, youtube, tiktok, whatsapp, telegram, linkedin. El dominio valida que la red este "
        "soportada, que no se repita y que la URL sea http(s)://. El resto de endpoints igual que en V-0.17.x."
    )

    pdf.chapter_title("3", "Modelo de datos - site_config (campo nuevo)")
    pdf.kv_table([
        ("redes_sociales_json", "TEXT - lista JSON de {red, url} (enlaces del pie publico)"),
    ])
    pdf.body(
        "El icono de cada red NO se guarda en BD: es un SVG self-hosted del frontend "
        "(app/config/redesSociales.tsx), asociado por el id de la red."
    )

    pdf.chapter_title("4", "Instalacion y despliegue")
    pdf.code(
        "cd plataforma-educativa\n"
        "cp .env.example .env   # APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY (>=32), admin\n"
        "docker compose up -d --build\n"
        "# El entrypoint corre alembic upgrade head: la migracion 015 anade redes_sociales_json."
    )

    pdf.chapter_title("5", "Seguridad y privacidad")
    pdf.bullet([
        "Iconos self-hosted: SVG incluidos en la app, NO de un CDN externo (no exponer IP de menores, §10).",
        "Enlaces salientes: abren en pestaña nueva con rel=noopener noreferrer (nh3 lo refuerza). Solo "
        "esquemas http/https/mailto; nunca javascript:.",
        "Sandbox/sanitizacion/menores: sin cambios (ejercicios aislados; HTML de articulos saneado; sin "
        "cuentas de alumno, sin cookies de seguimiento, visitas anonimas, sin perfilado).",
    ])

    pdf.chapter_title("6", "Tests")
    pdf.kv_table([
        ("Backend", "205 tests (unit + integracion)"),
        ("Redes sociales (V-0.18.0)", "defecto, actualizar, red no soportada, URL no web"),
        ("E2E (Playwright)", "9 flujos, incl. buscar y seguridad del sandbox"),
    ])
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

    pdf.chapter_title("7", "Apariencia - Redes sociales (novedad)")
    pdf.bullet([
        "Apariencia -> Ajustes generales -> seccion 'Redes sociales': pulsa '+ Anadir red social'.",
        "Elige la red en el desplegable (veras su icono) e introduce la URL de tu perfil (https://).",
        "Pulsa 'Guardar cambios': los iconos aparecen en el pie de la web publica (abren en pestaña nueva).",
        "Usa 'Quitar' para eliminar una red. Cada red puede anadirse una sola vez.",
    ])

    pdf.chapter_title("8", "Articulos - enlaces a terceros (novedad)")
    pdf.body(
        "En el editor de articulos, selecciona un texto (p. ej. el nombre de un autor) y pulsa el boton "
        "de enlace; pega la URL (puede ser un perfil de redes sociales de un tercero). Al publicarse, el "
        "enlace abre en una pestaña nueva de forma segura. El HTML del articulo se sanea siempre."
    )

    pdf.chapter_title("9", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.18.0)", "Redes sociales en el pie + enlaces a terceros en articulos."),
        ("Hecho (V-0.17.1)", "Robustez: migracion a PyJWT."),
        ("Pendiente robustez", "Backend como usuario no-root en Docker (gosu + chown; validar en servidor)."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.18.0.pdf")
    build_pdf(output)
