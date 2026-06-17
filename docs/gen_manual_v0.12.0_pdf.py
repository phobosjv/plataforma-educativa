# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.12.0.pdf usando fpdf2."""
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

VERSION = "V-0.12.0"
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
            "Esta version anade el LOGO DEL SITIO configurable: desde Apariencia se sube un "
            "logotipo (PNG, JPG, GIF o WebP) que se muestra junto al nombre en la cabecera publica "
            "y en el panel de administracion. La imagen se aloja en el propio origen y se sirve de "
            "forma segura (sin SVG, con nosniff); el campo logo_url solo admite referencias /media/.",
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
    pdf.section("Anadido: logo del sitio configurable")
    pdf.bullet([
        "Desde Apariencia -> Ajustes generales se sube un logotipo (PNG, JPG, GIF o WebP, max. 5 MB) "
        "con vista previa y boton para quitarlo. Se recomienda un PNG con fondo transparente.",
        "El logo aparece junto al nombre del sitio en la cabecera publica y en la barra lateral del "
        "panel de administracion. Sin logo, se muestra solo el nombre (igual que antes).",
        "La imagen se aloja en el propio origen (contexto media, direccionada por contenido SHA-256) "
        "y se sirve con X-Content-Type-Options: nosniff.",
        "El campo logo_url solo admite referencias al propio origen (/media/...): se rechaza una URL "
        "externa, evitando filtrar la IP de los menores a terceros (CLAUDE.md 10). SVG sigue rechazado.",
    ])
    pdf.section("Migraciones y notas")
    pdf.bullet([
        "Alembic 010 (site_config.logo_url).",
        "Esquemas API y cliente OpenAPI regenerados (logo_url en ConfiguracionResponse y ajustes generales).",
        "153 tests backend (4 nuevos del logo) en verde. Type-check de frontend limpio. API -> 0.12.0.",
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
        "y primaria en Espana. Acceso publico sin cuentas de alumno. Dos roles privilegiados: "
        "admin (configuracion + contenidos) y editor (gestion de contenidos)."
    )
    pdf.section("Caracteristicas principales")
    pdf.bullet([
        "Nombre, logotipo y paleta de colores configurables desde el panel de administracion.",
        "Frontend React MVP completo: catalogo, login, panel admin con todas las secciones.",
        "Taxonomia configurable: ciclos, cursos y asignaturas (incl. transversales -> Aula Abierta).",
        "Ejercicios ejecutados en iframe aislado con sandbox (sin acceso al origen padre).",
        "Articulos de texto con editor WYSIWYG (Tiptap) y HTML saneado en servidor.",
        "Fondos/estampados tematicos recoloreados con la paleta activa.",
        "Copias de seguridad automaticas de la BD + purga programada de papelera.",
    ])

    pdf.chapter_title("2", "Arquitectura del backend")
    pdf.section("Stack tecnologico")
    pdf.kv_table([
        ("Lenguaje", "Python 3.12+"),
        ("Framework API", "FastAPI"),
        ("ORM", "SQLAlchemy 2.0 (mapped_column)"),
        ("BD", "SQLite en modo WAL"),
        ("Migraciones", "Alembic"),
        ("Auth contrasenas", "Argon2id (argon2-cffi)"),
        ("Auth sesiones", "JWT HS256 (python-jose)"),
        ("Validacion", "Pydantic v2"),
    ])
    pdf.section("Contextos acotados implementados")
    pdf.kv_table([
        ("identity", "Usuarios (admin/editor), login JWT, guardas de rol"),
        ("content", "CRUD, versionado inmutable, papelera, articulos texto + ejercicios HTML"),
        ("taxonomy", "Ciclos, cursos y asignaturas (con flag transversal -> Aula Abierta)"),
        ("configuration", "Config del sitio: nombre, fuente, fondo, logo, paleta, paletas"),
        ("media", "Subida de imagenes (articulos y logo): raster, content-addressed, nosniff"),
    ])
    pdf.section("Regla de dependencia")
    pdf.body(
        "infrastructure -> application -> domain. "
        "El dominio no importa FastAPI, SQLAlchemy ni Pydantic de request. Jamas. "
        "Comunicacion entre contextos solo via casos de uso o eventos de dominio."
    )

    pdf.chapter_title("3", "Instalacion y despliegue")
    pdf.section("Arranque rapido con Docker (Caddy + HTTPS)")
    pdf.code(
        "cd plataforma-educativa\n"
        "cp .env.example .env\n"
        "# Editar: APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY, admin\n"
        "docker compose up -d --build\n"
        "docker compose logs -f caddy   # ver la emision de certificados\n"
        "# Web: https://APP_DOMAIN\n"
        "# El entrypoint ejecuta alembic upgrade head (migracion 010) + crea admin si no hay usuarios"
    )
    pdf.section("Arranque en desarrollo local")
    pdf.code(
        "cd backend && python -m alembic upgrade head\n"
        "uvicorn app.main:app --reload --port 8001\n\n"
        "cd frontend && npm install && npm run dev   # http://localhost:5173"
    )

    pdf.chapter_title("4", "Referencia de la API REST")
    pdf.body("Base URL: http://localhost:8001/api/v1  |  Formato: JSON  |  Auth: Bearer JWT")

    pdf.section("Media (/media/)")
    pdf.endpoint_table([
        ("POST", "/media/imagenes", "editor+", "Subir imagen raster (articulos y LOGO). Devuelve url /media/images/..."),
    ])

    pdf.section("Configuracion del sitio (/config/)")
    pdf.endpoint_table([
        ("GET", "/config/", "-", "Obtener config: nombre, fuente, fondo, logo, Aula Abierta, paleta"),
        ("PUT", "/config/general", "admin", "Cambiar nombre, fuente, fondo, logo y Aula Abierta"),
        ("PUT", "/config/paleta", "admin", "Activar paleta (predefinida o personalizada)"),
        ("POST", "/config/paletas", "admin", "Crear paleta personalizada"),
        ("PUT", "/config/paletas/{id}", "admin", "Actualizar paleta personalizada"),
        ("DELETE", "/config/paletas/{id}", "admin", "Eliminar paleta personalizada"),
    ])
    pdf.body(
        "El campo logo_url solo admite referencias al propio origen (/media/...) o cadena vacia. "
        "Una URL externa se rechaza con 400."
    )

    pdf.section("Mantenimiento (solo admin)")
    pdf.endpoint_table([
        ("GET", "/admin/backups", "admin", "Listar copias de seguridad existentes"),
        ("POST", "/admin/backups", "admin", "Crear una copia de seguridad ahora"),
        ("GET", "/admin/backups/{nombre}", "admin", "Descargar el fichero de una copia (adjunto)"),
        ("POST", "/admin/export", "admin", "Exportacion completa BD+media (.tar.gz, adjunto)"),
    ])

    pdf.chapter_title("5", "Modelo de datos")
    pdf.section("Tabla: site_config (singleton)")
    pdf.kv_table([
        ("id", "VARCHAR(36) PK fijo - '00000000-0000-0000-0000-000000000001'"),
        ("nombre_sitio", "VARCHAR(255) - nombre visible del sitio"),
        ("paleta_activa", "VARCHAR(100) - ID de la paleta activa"),
        ("paletas_json", "TEXT - JSON array con paletas personalizadas"),
        ("fuente_activa", "VARCHAR(100) - ID de la fuente activa (default 'sistema')"),
        ("fondo_activo", "VARCHAR(100) - ID del fondo/estampado (default 'ninguno')"),
        ("fondo_estilo", "VARCHAR(100) - disposicion del estampado (default 'ordenado')"),
        ("logo_url", "VARCHAR(500) - (V-0.12.0) URL del logo (/media/...) o vacio"),
        ("aula_abierta_label", "VARCHAR(40) - etiqueta de Aula Abierta (default 'Aula Abierta')"),
        ("aula_abierta_emoji", "VARCHAR(16) - emoji de Aula Abierta (default estrella)"),
    ])
    pdf.body(
        "Las tablas user, content, content_version, ciclo, curso y asignatura se mantienen sin "
        "cambios respecto a V-0.11.0 (asignatura.is_transversal de la migracion 008)."
    )

    pdf.chapter_title("6", "Seguridad")
    pdf.section("Aislamiento del sandbox y sanitizacion")
    pdf.bullet([
        "Ejercicios en iframe sandbox='allow-scripts' (SIN allow-same-origin), servidos desde "
        "sandbox.<dominio> con CSP estricta.",
        "HTML de articulos: SIEMPRE saneado (nh3 en servidor + DOMPurify en cliente).",
        "HTML de ejercicios: NO saneado (debe ejecutar JS); por eso va aislado.",
    ])
    pdf.section("Logo e imagenes")
    pdf.bullet([
        "Subidas raster (PNG/JPG/GIF/WebP), SIN SVG (vector XSS), direccionadas por contenido.",
        "Servidas con X-Content-Type-Options: nosniff desde el propio origen.",
        "logo_url solo referencia el propio origen (/media/...): nunca una URL externa.",
    ])
    pdf.section("Privacidad y proteccion de menores")
    pdf.bullet([
        "Sin cuentas de alumno, sin cookies de seguimiento, sin perfilado.",
        "Visitas anonimas y agregadas. Sin publicidad dirigida a menores (DSA art. 28).",
    ])

    pdf.chapter_title("7", "Tests")
    pdf.kv_table([
        ("Unitarios (dominio + handlers)", "mocks de repositorios, sin BD"),
        ("Integracion (endpoints)", "SQLite en memoria, TestClient FastAPI"),
        ("Logo (V-0.12.0)", "default vacio, actualizar, quitar, rechazo de URL externa"),
        ("Total", "153 tests - todos pasan en V-0.12.0"),
    ])
    pdf.code(
        "cd backend\n"
        "python -m pytest tests/unit tests/integration -q   # 153 tests"
    )

    # ---- PARTE II: MANUAL DE USUARIO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("8", "Apariencia - Logo del sitio (novedad)")
    pdf.body(
        "En Apariencia -> Ajustes generales, seccion 'Logo del sitio' (justo bajo el nombre):"
    )
    pdf.bullet([
        "Pulsar 'Subir logo' y elegir una imagen (PNG, JPG, GIF o WebP, max. 5 MB). Mejor PNG "
        "con fondo transparente.",
        "Se muestra una vista previa del logo.",
        "Pulsar 'Guardar cambios' para aplicarlo: aparece junto al nombre en la cabecera publica "
        "y en la barra lateral del panel admin.",
        "Para retirarlo, pulsar 'Quitar' y guardar; el sitio vuelve a mostrar solo el nombre.",
    ])
    pdf.body(
        "El logo se sube al propio servidor (no a un CDN externo) y se sirve de forma segura. "
        "Sin logo, la cabecera se ve igual que antes."
    )

    pdf.chapter_title("9", "Resto del panel")
    pdf.body(
        "Acceso publico (catalogo navegable), Contenidos (CRUD + papelera), Taxonomia (ciclos, "
        "cursos, asignaturas con transversales -> Aula Abierta), Apariencia (nombre, fuente, fondo, "
        "paletas, Aula Abierta) y Usuarios (solo admin) funcionan igual que en V-0.11.0."
    )

    pdf.chapter_title("10", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.12.0)", "Logo del sitio configurable."),
        ("Hecho (V-0.11.0)", "Asignaturas transversales / Aula Abierta."),
        ("Siguiente", "Buscador full-text (FTS5) en el catalogo publico."),
        ("Mas adelante", "Contador de visitas, auditoria, UI de versionado. Usuario no-root backend."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.12.0.pdf")
    build_pdf(output)
