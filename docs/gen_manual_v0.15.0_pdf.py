# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.15.0.pdf usando fpdf2."""
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

VERSION = "V-0.15.0"
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
            "Esta version anade la AUDITORIA (contexto auditing): registra todas las acciones de "
            "gestion de admin/editor (quien hizo que, sobre que objeto y cuando) y las muestra en una "
            "pagina del panel de administracion. El registro es append-only y se conserva indefinidamente.",
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
    pdf.section("Anadido: auditoria de acciones de gestion (contexto auditing)")
    pdf.bullet([
        "Registro de auditoria de todas las acciones de admin/editor: quien hizo que, sobre que objeto "
        "y cuando. Cubre contenidos (crear/editar/publicar/borrar/restaurar/purgar/subir HTML), "
        "usuarios, taxonomia (ciclos/cursos/asignaturas) y configuracion (ajustes y paletas).",
        "Pagina 'Auditoria' en el panel admin (solo admin): fecha, usuario (email + rol), accion, detalle.",
        "Endpoint GET /api/v1/auditoria (solo admin, paginado). Append-only; se conserva indefinidamente.",
        "Se escribe en la capa API tras cada accion con exito, con la sesion de la peticion. A prueba de "
        "fallos: si la auditoria fallara, nunca tumba la accion real del usuario.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "Nueva tabla audit_log (indice por fecha); migracion Alembic 013.",
        "186 tests backend (10 nuevos) + 9 E2E en verde. Type-check de frontend limpio. API -> 0.15.0.",
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
        "Nombre, logotipo y paleta configurables. Buscador del catalogo (full-text).",
        "Contador de visitas anonimas. Auditoria de acciones de gestion (quien, que, cuando).",
        "Taxonomia configurable: ciclos, cursos y asignaturas (incl. transversales -> Aula Abierta).",
        "Ejercicios en iframe aislado con sandbox; articulos con HTML saneado en servidor.",
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
        ("analytics", "Contador de visitas: buffer en memoria + volcado por lotes"),
        ("auditing", "Registro de acciones de gestion (append-only) + consulta para admin"),
    ])
    pdf.section("Como se registra la auditoria")
    pdf.body(
        "Cada router de gestion llama a registrar_auditoria(...) tras una accion con exito, con la "
        "MISMA sesion de la peticion (entrada coherente y testeable). Toma datos primitivos del usuario "
        "(id/email/rol) para no acoplar auditing a identity. El dominio define el puerto "
        "AuditoriaRepository; la infraestructura lo implementa. El registro es a prueba de fallos."
    )

    pdf.chapter_title("3", "Instalacion y despliegue")
    pdf.section("Arranque rapido con Docker (Caddy + HTTPS)")
    pdf.code(
        "cd plataforma-educativa\n"
        "cp .env.example .env   # APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY, admin\n"
        "docker compose up -d --build\n"
        "# El entrypoint corre alembic upgrade head: la migracion 013 crea audit_log."
    )
    pdf.section("Arranque en desarrollo local")
    pdf.code(
        "cd backend && python -m alembic upgrade head\n"
        "uvicorn app.main:app --reload --port 8001\n\n"
        "cd frontend && npm install && npm run dev   # http://localhost:5173"
    )

    pdf.chapter_title("4", "Referencia de la API REST")
    pdf.body("Base URL: http://localhost:8001/api/v1  |  Formato: JSON  |  Auth: Bearer JWT")
    pdf.section("Auditoria (/auditoria)")
    pdf.endpoint_table([
        ("GET", "/auditoria?limite=&offset=", "admin", "Acciones registradas, mas recientes primero"),
    ])
    pdf.section("Otros (sin cambios respecto a V-0.14.0)")
    pdf.endpoint_table([
        ("GET", "/contenidos/buscar?q=", "-", "Buscar por titulo/descripcion/etiquetas (FTS5)"),
        ("POST", "/analytics/visitas/{id}", "-", "Registrar visita anonima (buffer en memoria)"),
        ("GET", "/analytics/visitas", "admin", "Total de visitas + desglose por contenido"),
        ("POST", "/contenidos/", "editor+", "Crear contenido (auditado)"),
        ("POST", "/contenidos/{id}/publicar", "editor+", "Publicar (auditado)"),
    ])

    pdf.chapter_title("5", "Modelo de datos - audit_log")
    pdf.kv_table([
        ("id", "VARCHAR PK (UUID)"),
        ("usuario_id / usuario_email / usuario_rol", "Autor de la accion (email/rol copiados)"),
        ("accion", "crear, editar, publicar, borrar, restaurar, purgar, subir_html, ..."),
        ("entidad", "contenido, usuario, ciclo, curso, asignatura, configuracion"),
        ("entidad_id", "ID del objeto afectado (nullable)"),
        ("detalle", "Texto libre (p. ej. el titulo o nombre)"),
        ("created_at", "Fecha de la accion (indexada)"),
    ])
    pdf.body(
        "Append-only: no se edita ni se borra desde la aplicacion. El resto de tablas se mantienen "
        "como en V-0.14.0 (content_views, content_fts, etc.)."
    )

    pdf.chapter_title("6", "Seguridad y privacidad")
    pdf.bullet([
        "Sandbox: ejercicios en iframe sandbox='allow-scripts' (sin allow-same-origin), CSP estricta.",
        "Sanitizacion: HTML de articulos saneado siempre (nh3 + DOMPurify); ejercicios aislados.",
        "Auditoria: guarda email/rol del autor de cada accion de gestion. Solo admin la consulta. No "
        "registra acciones de visitantes anonimos.",
        "Menores: sin cuentas de alumno, sin cookies de seguimiento, visitas anonimas, sin perfilado.",
    ])

    pdf.chapter_title("7", "Tests")
    pdf.kv_table([
        ("Backend", "186 tests (unit + integracion)"),
        ("Auditoria (V-0.15.0)", "registro/consulta, accion deja entrada con autor, fallidas no, guarda admin"),
        ("E2E (Playwright)", "9 flujos, incl. buscar y seguridad del sandbox"),
    ])
    pdf.code(
        "cd backend && python -m pytest tests/unit tests/integration -q   # 186\n"
        "cd frontend && npm run test:e2e                                  # 9 E2E"
    )

    # ---- PARTE II: MANUAL DE USUARIO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("8", "Auditoria (novedad)")
    pdf.bullet([
        "Panel de admin -> seccion 'Auditoria' (solo admin): registro de las acciones de gestion mas "
        "recientes con fecha, usuario, accion y detalle.",
        "Se registra automaticamente al crear/editar/publicar/borrar/restaurar/eliminar contenidos, "
        "crear usuarios, gestionar la taxonomia o cambiar la configuracion.",
        "El registro NO se borra con el tiempo: queda como historial permanente.",
        "Las acciones que fallan (p. ej. borrar algo que no existe) no generan entrada.",
    ])

    pdf.chapter_title("9", "Resto del panel")
    pdf.body(
        "Acceso publico (catalogo + buscador), Contenidos (CRUD + papelera + visitas), Taxonomia, "
        "Apariencia (nombre, logo, fuente, fondo, paletas, Aula Abierta) y Usuarios (solo admin) "
        "funcionan igual que en V-0.14.0."
    )

    pdf.chapter_title("10", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.15.0)", "Auditoria de acciones de gestion (contexto auditing)."),
        ("Hecho (V-0.14.0)", "Contador de visitas (contexto analytics)."),
        ("Siguiente", "Donaciones configurables; publicidad en margenes (zona publica); frases configurables."),
        ("Mas adelante", "UI de versionado/restauracion. Usuario no-root en el backend."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.15.0.pdf")
    build_pdf(output)
