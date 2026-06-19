# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.21.5.pdf usando fpdf2."""
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

VERSION = "V-0.21.5"
FECHA = "2026-06-19"


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
            "Proxy inverso OPCIONAL para paneles de administracion del servidor via Caddy. Dos "
            "subdominios configurables en el .env (WEBMIN_DOMAIN y PORTAINER_DOMAIN) que Caddy sirve "
            "con HTTPS de Let's Encrypt y reenvia a Webmin (host, 10000) y Portainer (contenedor que "
            "publica 9443 en el host). Permite entrar sin el puerto y cerrar 10000/9443 a internet. "
            "Cambio solo de despliegue: sin tocar backend, API, esquema ni codigo de la aplicacion.",
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
    pdf.chapter_title("0", "Proxy inverso opcional para paneles de administracion")
    pdf.section("Que cambia")
    pdf.bullet([
        "Caddy sirve por HTTPS dos paneles externos al stack, via subdominios del .env: "
        "WEBMIN_DOMAIN (Webmin en el host, 10000) y PORTAINER_DOMAIN (Portainer, 9443 publicado).",
        "Entras por https://webmin... y https://portainer... sin el puerto; puedes cerrar 10000/9443.",
        "Solo despliegue: sin cambios de backend, API, esquema ni codigo de la aplicacion.",
    ])
    pdf.section("Opcionalidad")
    pdf.bullet([
        "Si no defines las variables, docker-compose pasa *.localhost y Caddy sirve ese bloque con su "
        "CA interna (no pide cert a Let's Encrypt): queda inerte y no afecta a otros despliegues.",
    ])

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE I - MANUAL TECNICO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("1", "Cambios")
    pdf.kv_table([
        ("caddy/Caddyfile", "Bloques WEBMIN_DOMAIN->10000 y PORTAINER_DOMAIN->9443 (tls_insecure_skip_verify)."),
        ("docker-compose.yml", "caddy recibe las 2 vars (default *.localhost) + extra_hosts host-gateway."),
        (".env.example", "Documenta WEBMIN_DOMAIN y PORTAINER_DOMAIN (opcionales)."),
    ])

    pdf.chapter_title("2", "Como funciona")
    pdf.body(
        "Webmin y Portainer exponen HTTPS con certificado autofirmado en su puerto; Caddy reenvia con "
        "tls_insecure_skip_verify (la verificacion interna se omite a proposito) y aporta el cifrado de "
        "cara a internet con su certificado de Let's Encrypt. host.docker.internal resuelve al host por "
        "el extra_hosts host-gateway: Webmin escucha en el host (10000) y Portainer publica el 9443 en "
        "el host, asi que ambos se alcanzan por esa ruta."
    )

    pdf.chapter_title("3", "Requisitos para activarlos")
    pdf.bullet([
        "DNS A de cada subdominio apuntando a la IP del servidor (CNAME al principal tambien vale).",
        "Portainer debe PUBLICAR el 9443 en el host (docker ps: 0.0.0.0:9443->9443/tcp).",
        "Webmin: si da error de referrer, anade el dominio en Webmin Configuration > Trusted Referrers.",
    ])

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("4", "Activar el acceso HTTPS a Webmin/Portainer")
    pdf.code(
        "# En el .env del servidor (los que uses):\n"
        "WEBMIN_DOMAIN=webmin.tudominio.com\n"
        "PORTAINER_DOMAIN=portainer.tudominio.com\n"
        "\n"
        "# Recargar Caddy:\n"
        "docker compose up -d caddy"
    )
    pdf.body(
        "Asegura el DNS de esos subdominios y que Portainer publica el 9443. Entra por https://webmin... "
        "y https://portainer...; Caddy emite el certificado al primer acceso. Tras comprobarlo, puedes "
        "cerrar 10000/9443 a internet en el firewall."
    )

    pdf.chapter_title("5", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.21.5)", "Proxy inverso opcional para Webmin/Portainer via Caddy."),
        ("Hecho (V-0.21.4)", "Tabla de contenidos: columnas de taxonomia, orden y paginacion."),
        ("Hecho (V-0.21.3)", "Seccion 'Monetizacion y RRSS' separada de 'Apariencia'."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.21.5.pdf")
    build_pdf(output)
