# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.16.0.pdf usando fpdf2."""
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

VERSION = "V-0.16.0"
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
            "Esta version anade tres ajustes configurables desde administracion: enlaces de DONACION "
            "(en el pie publico), PUBLICIDAD en los margenes (solo en las pantallas de navegacion del "
            "catalogo, nunca durante un ejercicio) y los TEXTOS de la portada del catalogo (dirigibles "
            "a las familias). Monetizacion ligera y solo en zonas de adultos (CLAUDE.md 10).",
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
        cols = [18, 78, 25, INNER_W - 18 - 78 - 25]
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
            self.set_font("Courier", "", 8)
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
    pdf.section("Anadido: donaciones, publicidad y textos del catalogo")
    pdf.bullet([
        "Enlaces de donacion (etiqueta + URL https://) configurables; se muestran como botones en el "
        "pie de la web publica. Se rechazan esquemas peligrosos (javascript:, ...).",
        "Publicidad (codigo HTML de la red de anuncios) en los margenes izq/der, SOLO en las pantallas "
        "de navegacion del catalogo. Nunca durante un ejercicio (lo usa un menor) ni en el panel admin.",
        "Textos de la portada del catalogo configurables: '¿En que curso estas?' (titulo) y 'Toca tu "
        "curso para ver las actividades' (subtitulo). Dirigibles a las familias si hay publicidad.",
        "site_config gana 6 columnas; migracion Alembic 014. Todo se guarda por PUT /config/general.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "Monetizacion ligera y solo en zonas de adultos (CLAUDE.md 10); sin perfilado (DSA art. 28).",
        "192 tests backend (6 nuevos) + 9 E2E en verde. Type-check de frontend limpio. API -> 0.16.0.",
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
        "Nombre, logotipo, paleta, textos de portada, donaciones y publicidad configurables.",
        "Buscador del catalogo (full-text). Contador de visitas anonimas. Auditoria de gestion.",
        "Ejercicios en iframe aislado con sandbox; articulos con HTML saneado en servidor.",
        "Taxonomia configurable: ciclos, cursos y asignaturas (incl. transversales -> Aula Abierta).",
        "Monetizacion ligera: donaciones (pie publico) y publicidad solo en zonas de adultos.",
    ])

    pdf.chapter_title("2", "Arquitectura del backend")
    pdf.section("Contextos acotados implementados")
    pdf.kv_table([
        ("identity", "Usuarios, login JWT, guardas de rol"),
        ("content", "CRUD, versionado, papelera, articulos + ejercicios, busqueda FTS5"),
        ("taxonomy", "Ciclos, cursos y asignaturas (transversal -> Aula Abierta)"),
        ("configuration", "Sitio: nombre, fuente, fondo, logo, paletas, textos, donaciones, publicidad"),
        ("media", "Subida de imagenes (articulos y logo)"),
        ("analytics", "Contador de visitas"),
        ("auditing", "Registro de acciones de gestion"),
    ])
    pdf.section("Donde se muestran donaciones y publicidad (frontend)")
    pdf.body(
        "Donaciones: botones en el pie (PublicLayout). Publicidad: rieles fijos en los margenes "
        "renderizados por PublicLayout SOLO cuando la ruta es el catalogo ('/'); asi ContenidoPage "
        "(/contenido/:id) queda sin anuncios y el panel admin (otro layout) tampoco los muestra. Los "
        "textos de portada los lee CatalogoPage de la configuracion."
    )

    pdf.chapter_title("3", "Instalacion y despliegue")
    pdf.section("Arranque rapido con Docker (Caddy + HTTPS)")
    pdf.code(
        "cd plataforma-educativa\n"
        "cp .env.example .env   # APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY, admin\n"
        "docker compose up -d --build\n"
        "# El entrypoint corre alembic upgrade head: la migracion 014 anade los campos nuevos."
    )
    pdf.section("Arranque en desarrollo local")
    pdf.code(
        "cd backend && python -m alembic upgrade head\n"
        "uvicorn app.main:app --reload --port 8001\n\n"
        "cd frontend && npm install && npm run dev   # http://localhost:5173"
    )

    pdf.chapter_title("4", "API - Configuracion (/config/)")
    pdf.endpoint_table([
        ("GET", "/config/", "-", "Config del sitio (incluye textos, donaciones y publicidad)"),
        ("PUT", "/config/general", "admin", "Actualiza todos los ajustes generales del sitio"),
        ("PUT", "/config/paleta", "admin", "Activar paleta"),
        ("POST/DEL", "/config/paletas[/{id}]", "admin", "CRUD de paletas personalizadas"),
    ])
    pdf.body(
        "Campos nuevos de GET /config/: catalogo_titulo, catalogo_subtitulo, donaciones (lista de "
        "{etiqueta,url}), publicidad_activa, publicidad_html_izquierda, publicidad_html_derecha. El "
        "resto de endpoints se mantienen como en V-0.15.0."
    )

    pdf.chapter_title("5", "Modelo de datos - site_config (campos nuevos)")
    pdf.kv_table([
        ("catalogo_titulo", "VARCHAR(120) - titulo de la portada del catalogo"),
        ("catalogo_subtitulo", "VARCHAR(120) - subtitulo de la portada"),
        ("donaciones_json", "TEXT - lista JSON de {etiqueta, url}"),
        ("publicidad_activa", "BOOLEAN - si se muestra la publicidad en navegacion"),
        ("publicidad_html_izquierda", "TEXT - codigo del anuncio del margen izquierdo"),
        ("publicidad_html_derecha", "TEXT - codigo del anuncio del margen derecho"),
    ])

    pdf.chapter_title("6", "Seguridad y privacidad")
    pdf.bullet([
        "Sandbox/sanitizacion: sin cambios (ejercicios aislados; HTML de articulos saneado).",
        "Donaciones: las URLs deben ser http(s)://; el dominio rechaza otros esquemas.",
        "Publicidad: el codigo lo introduce el admin (de confianza) y solo se muestra en zonas de "
        "adultos (navegacion), nunca durante la interaccion del menor con un ejercicio.",
        "Menores: sin cuentas de alumno, sin cookies de seguimiento, visitas anonimas, sin perfilado.",
    ])

    pdf.chapter_title("7", "Tests")
    pdf.kv_table([
        ("Backend", "192 tests (unit + integracion)"),
        ("Config (V-0.16.0)", "textos (defecto/cambio/vacio), donaciones (alta/URL no web), publicidad"),
        ("E2E (Playwright)", "9 flujos, incl. buscar y seguridad del sandbox"),
    ])
    pdf.code(
        "cd backend && python -m pytest tests/unit tests/integration -q   # 192\n"
        "cd frontend && npm run test:e2e                                  # 9 E2E"
    )

    # ---- PARTE II: MANUAL DE USUARIO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("8", "Apariencia - novedades")
    pdf.section("Textos de la portada del catalogo")
    pdf.body(
        "En Apariencia -> Ajustes generales, seccion 'Textos de la portada del catalogo': edita el "
        "titulo y el subtitulo de la pantalla inicial. Si activas la publicidad, conviene redactarlos "
        "dirigidos a las familias (es donde se ven los anuncios)."
    )
    pdf.section("Enlaces de donacion")
    pdf.body(
        "Seccion 'Enlaces de donacion': pulsa '+ Anadir enlace', escribe la etiqueta (p. ej. PayPal) y "
        "la URL (debe empezar por https://). Guarda. Aparecen como botones en el pie de la web publica. "
        "Usa 'Quitar' para eliminar uno."
    )
    pdf.section("Publicidad en los margenes")
    pdf.bullet([
        "Marca 'Mostrar publicidad...' y pega el codigo HTML de tu red de anuncios en el margen izq y/o der.",
        "Se muestra SOLO en las pantallas de navegacion del catalogo (elegir curso/asignatura/ejercicio).",
        "NO se muestra durante un ejercicio o articulo (lo usa un menor) ni en el panel admin.",
        "Se oculta en pantallas estrechas (movil) para no tapar el contenido.",
    ])

    pdf.chapter_title("9", "Resto del panel")
    pdf.body(
        "Sin cambios respecto a V-0.15.0 (Contenidos, Taxonomia, Usuarios, Copias, Auditoria, paletas, "
        "logo, fuente, fondo, Aula Abierta)."
    )

    pdf.chapter_title("10", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.16.0)", "Donaciones, publicidad en margenes y textos del catalogo configurables."),
        ("Hecho (V-0.15.0)", "Auditoria de acciones de gestion."),
        ("Siguiente", "UI de versionado/restauracion de contenidos."),
        ("Mas adelante", "Usuario no-root en el backend; revision de dependencias."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.16.0.pdf")
    build_pdf(output)
