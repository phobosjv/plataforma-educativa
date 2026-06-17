# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.19.0.pdf usando fpdf2."""
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

VERSION = "V-0.19.0"
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
            "Esta version agrupa dos mejoras de contenido: (1) los enlaces a redes sociales conocidas "
            "dentro del cuerpo de un articulo se muestran con el ICONO de marca de la red (mismo SVG "
            "self-hosted del pie); y (2) el historial de versiones muestra el AUTOR (email) de cada "
            "version. Ademas se verifico que la taxonomia esta bien codificada en UTF-8 (no habia datos "
            "corruptos).",
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
    pdf.section("Anadido: iconos de red en articulos")
    pdf.bullet([
        "Cuando un editor enlaza a un perfil de una red conocida (Facebook, Instagram, X, YouTube, "
        "TikTok, WhatsApp, Telegram, LinkedIn) en el cuerpo de un articulo, el enlace se muestra "
        "precedido por el ICONO de marca de esa red.",
        "La deteccion es por dominio del enlace; el icono es el mismo SVG self-hosted del pie (fuente "
        "unica en redesSociales.tsx, sin CDN externo, §10). Los enlaces externos abren en pestaña nueva "
        "con rel=noopener noreferrer.",
    ])
    pdf.section("Anadido: autor de cada version")
    pdf.bullet([
        "El historial de versiones de un contenido muestra una columna 'Autor' con el email de quien "
        "creo cada version.",
        "El email se resuelve en la capa API a partir de created_by via el caso de uso de identity, sin "
        "acoplar el dominio de contenido.",
    ])
    pdf.section("Aclarado: taxonomia")
    pdf.bullet([
        "Los nombres de ciclos/cursos/asignaturas estan bien codificados en UTF-8 en la base de datos; "
        "lo que parecia 'doble codificacion' era solo la consola de Windows (cp1252). No hay datos "
        "corruptos ni migracion de datos.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "205 tests backend + 9 E2E en verde. Type-check frontend limpio.",
        "VersionResponse gana el campo opcional created_by_email; cliente OpenAPI regenerado. SIN "
        "migracion de base de datos. API -> 0.19.0.",
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

    pdf.chapter_title("2", "API afectada por esta version")
    pdf.kv_table([
        ("GET /contenidos/{id}/versiones", "Cada version incluye created_by_email (string o null)"),
    ])
    pdf.body(
        "El resto del contrato es identico a V-0.18.x. La resolucion del email se hace listando los "
        "usuarios privilegiados (pocos) y mapeando id -> email en la capa de composicion de la API."
    )

    pdf.chapter_title("3", "Modelo de datos")
    pdf.body(
        "Sin cambios de esquema: NO hay migracion Alembic nueva. created_by_email se deriva en lectura "
        "del created_by ya almacenado en content_version. El icono de cada red no se guarda en base de "
        "datos: es un SVG del frontend asociado por el id de la red."
    )

    pdf.chapter_title("4", "Instalacion y despliegue")
    pdf.code(
        "cd plataforma-educativa\n"
        "cp .env.example .env   # APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY (>=32), admin\n"
        "docker compose up -d --build\n"
        "# El entrypoint corre alembic upgrade head. Esta version NO anade migraciones nuevas."
    )

    pdf.chapter_title("5", "Seguridad y privacidad")
    pdf.bullet([
        "Iconos self-hosted: SVG incluidos en la app, NO de un CDN externo (no exponer IP de menores, §10).",
        "Enlaces salientes del cuerpo: abren en pestaña nueva con rel=noopener noreferrer; HTML saneado "
        "siempre (nh3 + DOMPurify); solo esquemas http/https/mailto.",
        "Sandbox/sanitizacion/menores: sin cambios respecto a versiones anteriores.",
    ])

    pdf.chapter_title("6", "Tests")
    pdf.kv_table([
        ("Backend", "205 tests (unit + integracion)"),
        ("Versionado", "el historial expone created_by_email (autor de cada version)"),
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

    pdf.chapter_title("7", "Enlazar redes sociales en un articulo (editor)")
    pdf.bullet([
        "En el editor de articulos, selecciona el texto (p. ej. el nombre de un autor citado).",
        "Pulsa el boton de enlace y pega la URL del perfil (puede ser de un tercero).",
        "Al publicarse, si la URL es de una red conocida, el enlace se muestra con el icono de la red "
        "delante; siempre abre en pestaña nueva de forma segura.",
    ])

    pdf.chapter_title("8", "Ver el autor de cada version (editor/admin)")
    pdf.body(
        "En la edicion de un contenido, la seccion 'Historial de versiones' muestra ahora la columna "
        "'Autor' con el email de quien hizo cada version, junto al titulo y la fecha. Restaurar una "
        "version sigue sin destruir el historial (crea una version nueva)."
    )

    pdf.chapter_title("9", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.19.0)", "Iconos de red en articulos + autor de cada version."),
        ("Hecho (V-0.18.0)", "Redes sociales en el pie + enlaces a terceros en articulos."),
        ("Pendiente robustez", "Backend como usuario no-root en Docker (validar en servidor)."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.19.0.pdf")
    build_pdf(output)
