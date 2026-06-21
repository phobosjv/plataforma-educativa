# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.21.7.pdf usando fpdf2."""
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

VERSION = "V-0.21.7"
FECHA = "2026-06-21"


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
            "Release de DOCUMENTACION: empaqueta la plantilla reutilizable para exponer Webmin y "
            "Portainer por HTTPS detras de Caddy en cualquier servidor. La plantilla se creo justo "
            "despues de cerrar el zip de V-0.21.6 y por eso quedo fuera de el; este release la "
            "incluye. Sin cambios de backend, API, esquema ni codigo de la aplicacion.",
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

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 10, "NOVEDADES DE " + VERSION, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)
    pdf.chapter_title("0", "Plantilla portatil de proxy Webmin/Portainer")
    pdf.section("Que se anade")
    pdf.bullet([
        "docs/proxy-webmin-portainer.md: guia reutilizable para poner Webmin y Portainer tras "
        "un proxy inverso Caddy con HTTPS, en CUALQUIER servidor (no solo este proyecto).",
        "Incluye un prompt copy-paste portatil con un PASO 0 que descubre el contenedor de "
        "Portainer, la ruta real del Caddyfile y la red de Caddy, sin asumir rutas del proyecto.",
        "Enlazada desde docs/despliegue.md.",
        "Solo documentacion: sin cambios de backend, API, esquema ni codigo de la aplicacion.",
    ])
    pdf.section("Por que un release aparte")
    pdf.body(
        "La plantilla se creo en un commit posterior al zip de V-0.21.6, asi que ese paquete no la "
        "incluye. Empaquetarla como V-0.21.7 (PATCH de documentacion) la deja disponible dentro de "
        "un zip de distribucion versionado."
    )

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE I - LECCIONES CLAVE", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("1", "caddy reload no aplica la config en caliente")
    pdf.body(
        "Incluso 'docker compose exec caddy caddy reload' responde 'Valid configuration' pero sigue "
        "sirviendo la configuracion anterior. Solo 'docker compose restart caddy' activa los "
        "cambios. Esto causo horas de confusion probando configuraciones que no estaban vivas."
    )
    pdf.code("docker compose restart caddy   # NO 'caddy reload'")

    pdf.chapter_title("2", "Con upstream HTTPS, Caddy reescribe el Host")
    pdf.body(
        "Al hacer reverse_proxy https://host:puerto, Caddy manda al upstream el Host del propio "
        "upstream por defecto, no el del cliente. Hay que forzar header_up Host {host} para que el "
        "destino (por ejemplo la proteccion CSRF de Portainer) reciba el dominio publico y la "
        "comprobacion Host vs Origin cuadre."
    )
    pdf.code(
        "reverse_proxy portainer:9000 {\n"
        "    header_up Host {host}\n"
        "    header_up X-Forwarded-Host {host}\n"
        "    header_up X-Forwarded-Proto https\n"
        "}"
    )

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - ROADMAP", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("3", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.21.7)", "Plantilla portatil de proxy Webmin/Portainer empaquetada."),
        ("Hecho (V-0.21.6)", "Proxy de Portainer por red interna + script + guia de despliegue."),
        ("Hecho (V-0.21.5)", "Proxy inverso opcional Webmin/Portainer via Caddy."),
        ("Backlog", "Tercer tipo de contenido: ficheros PDF (ficha imprimible/descargable)."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.21.7.pdf")
    build_pdf(output)
