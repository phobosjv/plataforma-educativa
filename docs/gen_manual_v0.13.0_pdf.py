# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.13.0.pdf usando fpdf2."""
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

VERSION = "V-0.13.0"
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
            "Esta version anade el BUSCADOR del catalogo (full-text, FTS5): un cuadro de busqueda en "
            "la portada que encuentra contenidos por titulo, descripcion y etiquetas, ignorando "
            "acentos y buscando por prefijo. El indice content_fts se mantiene con triggers y se "
            "consulta de forma segura frente a lo que escriba el usuario.",
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
    pdf.section("Anadido: buscador del catalogo (full-text, FTS5)")
    pdf.bullet([
        "Cuadro de busqueda en la portada que encuentra contenidos por titulo, descripcion y "
        "etiquetas. Resultados ordenados por relevancia, con su pantalla (estado en la URL ?q=).",
        "Pensado para ninos: ignora acentos en ambos sentidos (buscar 'espana' encuentra 'Espana') "
        "y busca por prefijo (escribir 'mapa' encuentra 'mapas'). Varios terminos combinan en AND.",
        "Nuevo endpoint publico GET /api/v1/contenidos/buscar?q=... (sin auth; solo publicado y no "
        "borrado; max. 50 resultados).",
        "Tabla virtual FTS5 content_fts (contenido externo sobre content) mantenida por triggers; "
        "migracion Alembic 011. La consulta neutraliza los operadores de FTS5 que escriba el usuario.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "164 tests backend (11 nuevos de busqueda) + 9 E2E (2 nuevos del buscador) en verde.",
        "Type-check de frontend limpio. Cliente OpenAPI regenerado. API -> 0.13.0.",
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
        "(HTML/CSS/JS autocontenidos) y articulos de texto, dirigidos a alumnado de infantil "
        "y primaria en Espana. Acceso publico sin cuentas de alumno. Dos roles: admin y editor."
    )
    pdf.section("Caracteristicas principales")
    pdf.bullet([
        "Nombre, logotipo y paleta de colores configurables desde el panel de administracion.",
        "Buscador del catalogo (full-text) por titulo, descripcion y etiquetas.",
        "Taxonomia configurable: ciclos, cursos y asignaturas (incl. transversales -> Aula Abierta).",
        "Ejercicios ejecutados en iframe aislado con sandbox (sin acceso al origen padre).",
        "Articulos de texto con editor WYSIWYG (Tiptap) y HTML saneado en servidor.",
        "Copias de seguridad automaticas de la BD + purga programada de papelera.",
    ])

    pdf.chapter_title("2", "Arquitectura del backend")
    pdf.section("Stack tecnologico")
    pdf.kv_table([
        ("Lenguaje", "Python 3.12+"),
        ("Framework API", "FastAPI"),
        ("ORM", "SQLAlchemy 2.0 (mapped_column)"),
        ("BD", "SQLite en modo WAL (busqueda con FTS5)"),
        ("Migraciones", "Alembic"),
        ("Auth", "Argon2id (contrasenas) + JWT HS256 (sesiones)"),
    ])
    pdf.section("Contextos acotados implementados")
    pdf.kv_table([
        ("identity", "Usuarios (admin/editor), login JWT, guardas de rol"),
        ("content", "CRUD, versionado, papelera, articulos + ejercicios, busqueda FTS5"),
        ("taxonomy", "Ciclos, cursos y asignaturas (con flag transversal -> Aula Abierta)"),
        ("configuration", "Config del sitio: nombre, fuente, fondo, logo, paleta, paletas"),
        ("media", "Subida de imagenes (articulos y logo): raster, content-addressed, nosniff"),
    ])
    pdf.section("Regla de dependencia")
    pdf.body(
        "infrastructure -> application -> domain. El dominio no importa FastAPI, SQLAlchemy ni "
        "Pydantic de request. La busqueda es un puerto del repositorio implementado en infraestructura."
    )

    pdf.chapter_title("3", "Instalacion y despliegue")
    pdf.section("Arranque rapido con Docker (Caddy + HTTPS)")
    pdf.code(
        "cd plataforma-educativa\n"
        "cp .env.example .env   # APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY, admin\n"
        "docker compose up -d --build\n"
        "docker compose logs -f caddy\n"
        "# Web: https://APP_DOMAIN\n"
        "# El entrypoint corre alembic upgrade head: la migracion 011 crea content_fts y, con\n"
        "# 'rebuild', INDEXA el contenido ya existente (sin pasos manuales ni perdida)."
    )
    pdf.section("Arranque en desarrollo local")
    pdf.code(
        "cd backend && python -m alembic upgrade head\n"
        "uvicorn app.main:app --reload --port 8001\n\n"
        "cd frontend && npm install && npm run dev   # http://localhost:5173"
    )

    pdf.chapter_title("4", "Referencia de la API REST")
    pdf.body("Base URL: http://localhost:8001/api/v1  |  Formato: JSON  |  Auth: Bearer JWT")
    pdf.section("Contenidos (/contenidos/)")
    pdf.endpoint_table([
        ("GET", "/contenidos/", "-", "Listar contenidos publicados (catalogo publico)"),
        ("GET", "/contenidos/buscar?q=", "-", "Buscar por titulo/descripcion/etiquetas (FTS5). Max 50"),
        ("GET", "/contenidos/{id}", "-", "Obtener contenido por ID"),
        ("POST", "/contenidos/", "editor+", "Crear contenido (sanea body_html de texto)"),
        ("PUT", "/contenidos/{id}", "editor+", "Actualizar (re-sanea body_html de texto)"),
        ("POST", "/contenidos/{id}/html", "editor+", "Subir HTML de ejercicio (multipart)"),
        ("DELETE", "/contenidos/{id}/purgar", "admin", "Eliminar definitivamente (desde papelera)"),
    ])
    pdf.body(
        "El endpoint /contenidos/buscar se declara ANTES de /contenidos/{id} para que el segmento "
        "'buscar' no se valide como UUID. Una q vacia o sin terminos utiles devuelve []."
    )

    pdf.chapter_title("5", "Modelo de datos - indice de busqueda")
    pdf.section("Tabla virtual content_fts (FTS5, contenido externo)")
    pdf.code(
        "CREATE VIRTUAL TABLE content_fts USING fts5(\n"
        "  titulo, descripcion, tags_json,\n"
        "  content='content', content_rowid='rowid',\n"
        "  tokenize='unicode61 remove_diacritics 2'\n"
        ");"
    )
    pdf.bullet([
        "No duplica datos: lee de content por rowid.",
        "Triggers content_fts_ai/ad/au mantienen el indice en alta/baja/modificacion.",
        "La consulta une content_fts con content para filtrar publicado/no borrado y ordenar por rank.",
        "El texto del usuario se convierte en '\"termino\"*' por palabra: prefijo, AND, sin operadores.",
    ])
    pdf.body(
        "El resto de tablas (user, content, content_version, ciclo, curso, asignatura, site_config) "
        "se mantienen como en V-0.12.0 (site_config.logo_url de la migracion 010)."
    )

    pdf.chapter_title("6", "Seguridad")
    pdf.section("Aislamiento, sanitizacion y busqueda")
    pdf.bullet([
        "Ejercicios en iframe sandbox='allow-scripts' (SIN allow-same-origin), CSP estricta.",
        "HTML de articulos: SIEMPRE saneado (nh3 + DOMPurify). HTML de ejercicios: aislado, no saneado.",
        "Busqueda: cada termino se entrecomilla, neutralizando operadores FTS5 y errores de sintaxis.",
        "Sin cuentas de alumno, sin cookies de seguimiento, sin perfilado (DSA art. 28).",
    ])

    pdf.chapter_title("7", "Tests")
    pdf.kv_table([
        ("Backend", "164 tests (unit + integracion)"),
        ("Busqueda (V-0.13.0)", "prefijo, acentos, descripcion/etiqueta, AND, no publicados/borrados, triggers"),
        ("E2E (Playwright)", "9 flujos, incl. buscar y seguridad del sandbox"),
    ])
    pdf.code(
        "cd backend && python -m pytest tests/unit tests/integration -q   # 164\n"
        "cd frontend && npm run test:e2e                                  # 9 E2E"
    )

    # ---- PARTE II: MANUAL DE USUARIO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("8", "Buscar en el catalogo (novedad)")
    pdf.body("En la portada del catalogo hay un cuadro de busqueda:")
    pdf.bullet([
        "Escribir una o varias palabras (p. ej. 'mapa', 'sumas', 'comunidades'). Sin tildes vale.",
        "Pulsar 'Buscar' (o Enter).",
        "Aparece la pantalla de resultados, ordenados por relevancia. Cada tarjeta abre su contenido.",
        "Si no hay coincidencias, se muestra un mensaje para probar con otra palabra.",
        "La busqueda queda en la direccion (?q=...): se puede compartir o recargar.",
    ])
    pdf.body(
        "Busca en el titulo, la descripcion y las etiquetas del contenido publicado. Busca por prefijo "
        "(escribir 'mapa' tambien encuentra 'mapas') y, con varias palabras, exige que aparezcan todas."
    )

    pdf.chapter_title("9", "Resto del panel")
    pdf.body(
        "Acceso publico (catalogo navegable), Contenidos (CRUD + papelera), Taxonomia, Apariencia "
        "(nombre, logo, fuente, fondo, paletas, Aula Abierta) y Usuarios (solo admin) funcionan igual "
        "que en V-0.12.0."
    )

    pdf.chapter_title("10", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.13.0)", "Buscador full-text (FTS5) del catalogo."),
        ("Hecho (V-0.12.0)", "Logo del sitio configurable."),
        ("Siguiente", "Contador de visitas (contexto analytics)."),
        ("Mas adelante", "Auditoria, UI de versionado. Usuario no-root en el backend."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.13.0.pdf")
    build_pdf(output)
