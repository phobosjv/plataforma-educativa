# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.23.2.pdf usando fpdf2."""
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

VERSION = "V-0.23.2"
FECHA = "2026-06-22"


class ManualPDF(FPDF):

    def header(self) -> None:
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*INDIGO)
        self.cell(0, 8, "Plataforma Educativa - Manual Tecnico y de Usuario  " + VERSION, align="L")
        self.set_text_color(*BLACK)
        self.ln(0)
        self.set_draw_color(*INDIGO)
        self.set_line_width(0.4)
        self.line(MARGIN, self.get_y() + 1, PAGE_W - MARGIN, self.get_y() + 1)
        self.ln(6)

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {{nb}} | {VERSION} - {FECHA}", align="C")

    def cover(self) -> None:
        self.add_page()
        self.set_fill_color(*INDIGO)
        self.rect(0, 0, PAGE_W, 80, "F")
        self.set_y(22)
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(*WHITE)
        self.cell(0, 12, "Plataforma Educativa", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 14)
        self.cell(0, 8, "Manual Tecnico y de Usuario", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, VERSION + "  |  " + FECHA, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*BLACK)
        self.ln(60)
        self.set_font("Helvetica", "", 10)
        self.set_x(MARGIN)
        self.multi_cell(INNER_W, 5.5,
            "Sistema CMS educativo para alojar ejercicios interactivos, articulos de texto y "
            "fichas PDF, dirigido a alumnado de infantil y primaria. Acceso publico sin cuentas "
            "de alumno. Roles admin y editor para la gestion de contenidos. Desplegado con Docker "
            "y Caddy (HTTPS automatico). Instalable como PWA en moviles y tablets."
        )

    def chapter_title(self, num: str, title: str) -> None:
        self.set_fill_color(*INDIGO_LIGHT)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*INDIGO)
        self.set_x(MARGIN)
        self.cell(INNER_W, 9, f"  {num}.  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*BLACK)
        self.ln(3)

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

    pdf.chapter_title("1", "Terminal de Webmin tras el proxy Caddy (fix)")
    pdf.body(
        "El terminal de Webmin (acceso tipo SSH por navegador) servido detras del proxy Caddy se "
        "quedaba en 'CONNECTING...'. La causa eran DOS problemas encadenados, ya resueltos:"
    )
    pdf.bullet([
        "Caddy no completaba el upgrade del WebSocket contra el upstream HTTPS de Webmin: el "
        "WebSocket (RFC 6455) necesita HTTP/1.1 y sobre HTTPS Caddy podia negociar otra version "
        "(el WS salia 'Finished'/0 B en vez de '101'). Fix: 'versions 1.1' en el transport http del "
        "bloque de Webmin del Caddyfile, mas header_up Host {host} y X-Forwarded-Proto/Host.",
        "Webmin rechazaba el origen ('Invalid Websockets origin'): su lista de origenes permitidos "
        "no se alimenta del Host ni de los referers. La pieza que faltaba es del lado Webmin (host): "
        "websocket_extra_origins=https://webmin.<dominio> en /etc/webmin/miniserv.conf.",
    ])
    pdf.body(
        "Confirmado funcionando en el servidor. El detalle, el diagnostico y la plantilla portatil "
        "para otros servidores con el mismo patron estan en docs/proxy-webmin-portainer.md."
    )

    pdf.chapter_title("2", "Aplicacion")
    pdf.body(
        "Parte Caddy (va en el zip): redesplegar y reiniciar Caddy con 'docker compose restart caddy' "
        "(NO 'caddy reload', que puede no aplicar la config). Parte Webmin (en el host, una sola vez, "
        "como redirect_ssl/referers): anadir websocket_extra_origins a /etc/webmin/miniserv.conf y "
        "'systemctl restart webmin'. No hay cambios en la aplicacion ni en la base de datos."
    )

    pdf.chapter_title("3", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.23.2)", "Fix terminal de Webmin (WebSocket) tras el proxy Caddy."),
        ("Hecho (V-0.23.1)", "Fix icono PWA (circulo blanco) + iconos derivados del logo."),
        ("Hecho (V-0.23.0)", "PWA instalable: manifiesto dinamico, service worker, iconos."),
        ("Hecho (V-0.22.0)", "Tercer tipo de contenido: ficha PDF imprimible."),
        ("Pendiente", "Cache offline (lectura de articulos sin conexion) - V-0.24.0+."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.23.2.pdf")
    build_pdf(output)
