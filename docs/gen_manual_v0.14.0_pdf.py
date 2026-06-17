# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.14.0.pdf usando fpdf2."""
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

VERSION = "V-0.14.0"
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
            "Esta version anade el CONTADOR DE VISITAS (contexto analytics): cuenta las visitas "
            "anonimas a cada contenido agregando en memoria y volcando por lotes a la BD (nunca una "
            "escritura por peticion), y muestra los totales en el panel de administracion. Visitas "
            "anonimas y agregadas, sin datos del visitante.",
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
    pdf.section("Anadido: contador de visitas (contexto analytics)")
    pdf.bullet([
        "Conteo de visitas anonimas: al abrir la ficha de un contenido se registra una visita. El "
        "panel de admin muestra las visitas totales (Inicio) y por contenido (lista de Contenidos).",
        "Diseno (CLAUDE.md 8): se agrega en memoria (buffer de proceso, thread-safe) y se vuelca por "
        "lotes a la BD (por defecto cada 5 min) y al apagar la app. Nunca una escritura por peticion.",
        "Privacidad (10): visitas anonimas y agregadas; solo un total por contenido, sin datos del "
        "visitante. La lectura del desglose es solo para admin.",
        "Endpoints: POST /analytics/visitas/{id} (publico, solo buffer) y GET /analytics/visitas "
        "(admin, total + desglose). Nueva tabla content_views; migracion Alembic 012.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "176 tests backend (12 nuevos de visitas) + 9 E2E en verde. Type-check de frontend limpio.",
        "Nuevos ajustes: analytics_enabled, analytics_flush_interval_seconds. API -> 0.14.0.",
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
        "Contador de visitas anonimas y agregadas por contenido.",
        "Ejercicios en iframe aislado con sandbox; articulos con HTML saneado en servidor.",
        "Taxonomia configurable: ciclos, cursos y asignaturas (incl. transversales -> Aula Abierta).",
        "Copias de seguridad automaticas de la BD + purga programada de papelera.",
    ])

    pdf.chapter_title("2", "Arquitectura del backend")
    pdf.section("Contextos acotados implementados")
    pdf.kv_table([
        ("identity", "Usuarios (admin/editor), login JWT, guardas de rol"),
        ("content", "CRUD, versionado, papelera, articulos + ejercicios, busqueda FTS5"),
        ("taxonomy", "Ciclos, cursos y asignaturas (con flag transversal -> Aula Abierta)"),
        ("configuration", "Config del sitio: nombre, fuente, fondo, logo, paleta, paletas"),
        ("media", "Subida de imagenes (articulos y logo): raster, content-addressed, nosniff"),
        ("analytics", "Contador de visitas: buffer en memoria + volcado por lotes a content_views"),
    ])
    pdf.section("Conteo de visitas (CLAUDE.md 8)")
    pdf.body(
        "El endpoint publico de registro solo incrementa un buffer en memoria (singleton de proceso, "
        "seguro para concurrencia). Una tarea de mantenimiento drena el buffer y suma los conteos a "
        "content_views por lotes (por defecto cada 5 min) y tambien al apagar la app, de modo que NUNCA "
        "hay una escritura en BD por peticion. La regla de dependencia se mantiene: el dominio define "
        "los puertos BufferVisitas y VisitasRepository, implementados en infraestructura."
    )

    pdf.chapter_title("3", "Instalacion y despliegue")
    pdf.section("Arranque rapido con Docker (Caddy + HTTPS)")
    pdf.code(
        "cd plataforma-educativa\n"
        "cp .env.example .env   # APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY, admin\n"
        "docker compose up -d --build\n"
        "# El entrypoint corre alembic upgrade head: la migracion 012 crea content_views.\n"
        "# Ajustes opcionales: ANALYTICS_ENABLED (true), ANALYTICS_FLUSH_INTERVAL_SECONDS (300)."
    )
    pdf.section("Arranque en desarrollo local")
    pdf.code(
        "cd backend && python -m alembic upgrade head\n"
        "uvicorn app.main:app --reload --port 8001\n\n"
        "cd frontend && npm install && npm run dev   # http://localhost:5173"
    )

    pdf.chapter_title("4", "Referencia de la API REST")
    pdf.body("Base URL: http://localhost:8001/api/v1  |  Formato: JSON  |  Auth: Bearer JWT")
    pdf.section("Analytics - visitas (/analytics/)")
    pdf.endpoint_table([
        ("POST", "/analytics/visitas/{id}", "-", "Registrar visita anonima (solo buffer en memoria)"),
        ("GET", "/analytics/visitas", "admin", "Total de visitas + desglose por contenido"),
    ])
    pdf.section("Contenidos (/contenidos/)")
    pdf.endpoint_table([
        ("GET", "/contenidos/", "-", "Listar contenidos publicados (catalogo)"),
        ("GET", "/contenidos/buscar?q=", "-", "Buscar por titulo/descripcion/etiquetas (FTS5)"),
        ("GET", "/contenidos/{id}", "-", "Obtener contenido por ID"),
        ("POST", "/contenidos/", "editor+", "Crear contenido (sanea body_html de texto)"),
        ("POST", "/contenidos/{id}/html", "editor+", "Subir HTML de ejercicio (multipart)"),
        ("DELETE", "/contenidos/{id}/purgar", "admin", "Eliminar definitivamente (desde papelera)"),
    ])

    pdf.chapter_title("5", "Modelo de datos - content_views")
    pdf.kv_table([
        ("content_id", "VARCHAR PK - id del contenido (no FK; si se purga, fila huerfana inocua)"),
        ("total", "INTEGER - total acumulado de visitas"),
        ("updated_at", "DATETIME - ultimo volcado que la modifico"),
    ])
    pdf.body(
        "El volcado usa INSERT ... ON CONFLICT(content_id) DO UPDATE SET total = total + n: crea la "
        "fila la primera vez y ACUMULA en los volcados sucesivos. El resto de tablas se mantienen como "
        "en V-0.13.0 (incluida la tabla virtual FTS5 content_fts)."
    )

    pdf.chapter_title("6", "Seguridad y privacidad")
    pdf.bullet([
        "Sandbox: ejercicios en iframe sandbox='allow-scripts' (sin allow-same-origin), CSP estricta.",
        "Sanitizacion: HTML de articulos saneado siempre (nh3 + DOMPurify); ejercicios aislados.",
        "Visitas: anonimas y agregadas; solo un total por contenido, sin IP ni identificadores. La "
        "lectura del desglose es solo admin. Sin cookies de seguimiento ni perfilado (DSA art. 28).",
        "Autenticacion: Argon2id + JWT HS256 con expiracion.",
    ])

    pdf.chapter_title("7", "Tests")
    pdf.kv_table([
        ("Backend", "176 tests (unit + integracion)"),
        ("Visitas (V-0.14.0)", "buffer, volcado por lotes (acumula), consulta, beacon sin BD, guarda admin"),
        ("E2E (Playwright)", "9 flujos, incl. buscar y seguridad del sandbox"),
    ])
    pdf.code(
        "cd backend && python -m pytest tests/unit tests/integration -q   # 176\n"
        "cd frontend && npm run test:e2e                                  # 9 E2E"
    )

    # ---- PARTE II: MANUAL DE USUARIO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("8", "Contador de visitas (novedad)")
    pdf.bullet([
        "Cada vez que un visitante abre la ficha de un contenido, se cuenta UNA visita. No se registra "
        "ningun dato de la persona: es un contador anonimo.",
        "Panel de admin -> Inicio: tarjeta 'Visitas totales' con la suma de todas las visitas.",
        "Panel de admin -> Contenidos: columna 'Visitas' con el total de cada contenido.",
        "Los numeros se actualizan POR LOTES (no al instante): el sistema acumula y guarda cada pocos "
        "minutos para no sobrecargar la BD; tras un repunte, el panel puede tardar un momento.",
    ])

    pdf.chapter_title("9", "Resto del panel")
    pdf.body(
        "Acceso publico (catalogo navegable + buscador), Contenidos (CRUD + papelera), Taxonomia, "
        "Apariencia (nombre, logo, fuente, fondo, paletas, Aula Abierta) y Usuarios (solo admin) "
        "funcionan igual que en V-0.13.0."
    )

    pdf.chapter_title("10", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.14.0)", "Contador de visitas (contexto analytics)."),
        ("Hecho (V-0.13.0)", "Buscador full-text (FTS5) del catalogo."),
        ("Siguiente", "Auditoria (contexto auditing) de acciones de admin/editor."),
        ("Mas adelante", "UI de versionado/restauracion. Usuario no-root en el backend."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.14.0.pdf")
    build_pdf(output)
