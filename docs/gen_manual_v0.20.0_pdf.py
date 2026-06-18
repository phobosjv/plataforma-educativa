# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.20.0.pdf usando fpdf2."""
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

VERSION = "V-0.20.0"
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
            "Importar / restaurar el sitio: operacion inversa de 'Exportar todo'. El administrador sube "
            "el .tar.gz de exportacion (BD + media + manifest) y el sitio destino queda restaurado o "
            "migrado con ese contenido (poner en marcha una web en blanco o recuperar tras un fallo "
            "total). Es destructivo: exige escribir IMPORTAR, crea una copia de seguridad previa y migra "
            "la BD al esquema actual (alembic upgrade head).",
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
        col1 = 70
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
    pdf.chapter_title("0", "Importar / restaurar el sitio")
    pdf.section("Que hace")
    pdf.bullet([
        "Operacion inversa de 'Exportar todo': sube el .tar.gz (BD + media + manifest) y el sitio "
        "destino queda restaurado/migrado con ese contenido.",
        "Casos de uso: poner en marcha una web en blanco con el contenido de otra (migracion), o "
        "recuperar tras un fallo total.",
    ])
    pdf.section("Seguridad")
    pdf.bullet([
        "Destructivo: reemplaza la BD y restaura la media. Exige escribir IMPORTAR para confirmar.",
        "Crea AUTOMATICAMENTE una copia de seguridad de la BD actual antes de sobrescribir (rollback).",
        "Tras importar, alembic upgrade head migra el esquema: una exportacion antigua queda migrada.",
        "La sesion del admin puede invalidarse (el usuario viene de la BD importada): se vuelve al "
        "login para entrar con las credenciales del sitio importado.",
    ])
    pdf.section("Notas")
    pdf.bullet([
        "Cliente OpenAPI regenerado (nuevo endpoint). SIN migracion propia de esta version.",
        "211 tests backend (6 nuevos de import) + 9 E2E en verde. Type-check frontend limpio.",
    ])

    # ---- PARTE I: MANUAL TECNICO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE I - MANUAL TECNICO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("1", "API")
    pdf.kv_table([
        ("POST /admin/import (admin)", "multipart: fichero (.tar.gz) + confirmacion=IMPORTAR"),
        ("POST /admin/export (admin)", "(existente) genera y descarga el .tar.gz"),
    ])
    pdf.body(
        "Respuesta de import: ok, num_ficheros_media, app_version_importada, backup_seguridad, detalle."
    )

    pdf.chapter_title("2", "Como funciona (ImportService)")
    pdf.bullet([
        "Extraccion segura: solo data/, media/ y manifest.json; rechaza rutas absolutas o con '..' "
        "(sin path traversal); ignora enlaces y dispositivos.",
        "Validacion: manifest.formato soportado + integridad SQLite (PRAGMA integrity_check).",
        "Copia de seguridad de la BD actual (rollback) antes de tocar nada.",
        "Cierra conexiones del pool (engine.dispose()).",
        "Restaura media (mezcla; ficheros content-addressed inmutables).",
        "Intercambio atomico del fichero de BD con os.replace (rename); elimina -wal/-shm obsoletos.",
        "Despues, alembic upgrade head migra el esquema si la exportacion era de una version anterior.",
    ])

    pdf.chapter_title("3", "Modelo de datos")
    pdf.body("Sin cambios de esquema propios de esta version: NO hay migracion nueva.")

    pdf.chapter_title("4", "Tests")
    pdf.code(
        "cd backend && python -m pytest tests/unit tests/integration -q   # 211 (6 de import)\n"
        "cd frontend && npm run test:e2e                                  # 9 E2E"
    )
    pdf.body(
        "Cobertura de import: requiere admin (401/403), confirmacion obligatoria, archivo invalido, "
        "manifest no soportado y un round-trip export->import que verifica BD y media restauradas."
    )

    # ---- PARTE II: MANUAL DE USUARIO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("5", "Migrar o restaurar el sitio (admin)")
    pdf.bullet([
        "En el sitio de ORIGEN: 'Copias de seguridad' -> 'Exportar todo (BD + media)'; guarda el .tar.gz.",
        "En el sitio de DESTINO (puede estar en blanco): 'Copias de seguridad' -> seccion 'Importar / "
        "restaurar el sitio'.",
        "Selecciona el .tar.gz, escribe IMPORTAR en el cuadro de confirmacion y pulsa 'Importar y "
        "reemplazar el sitio'.",
        "Al terminar se cierra la sesion: entra con las credenciales del sitio importado. La web queda "
        "con el contenido, la configuracion, los usuarios y la media del origen.",
    ])
    pdf.body(
        "Antes de sobrescribir se guarda una copia de seguridad de la base de datos actual, por si "
        "necesitas revertir."
    )

    pdf.chapter_title("6", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.20.0)", "Importar / restaurar el sitio (BD + media) desde una exportacion."),
        ("Hecho (V-0.19.2)", "Pie publico y acciones de admin/editor siempre visibles."),
        ("Hecho (V-0.19.1)", "Backend sin privilegios (no-root) en Docker."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.20.0.pdf")
    build_pdf(output)
