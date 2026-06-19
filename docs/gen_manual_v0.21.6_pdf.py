# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.21.6.pdf usando fpdf2."""
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

VERSION = "V-0.21.6"
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
            "Cambio de despliegue: afina el proxy inverso de PORTAINER detras de Caddy para que "
            "funcione de verdad (evita el error CSRF 'Forbidden - origin invalid' y el doble TLS) y "
            "documenta la PRIMERA INSTALACION en un servidor recien instalado. Portainer se alcanza "
            "ahora por la red interna del stack (portainer:9000) en lugar de host.docker.internal:9443. "
            "Sin tocar backend, API, esquema ni codigo de la aplicacion.",
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
    pdf.chapter_title("0", "Proxy inverso de Portainer (arreglo) + guia de despliegue")
    pdf.section("Que cambia")
    pdf.bullet([
        "El bloque PORTAINER_DOMAIN deja de usar host.docker.internal:9443 y pasa a "
        "reverse_proxy portainer:9000 (HTTP, red interna del stack, por nombre de contenedor), "
        "forzando el Host publico con header_up.",
        "Nuevo script connect-portainer.sh: conecta el contenedor 'portainer' (externo al stack) "
        "a la red de Caddy. Se ejecuta UNA vez tras desplegar; es idempotente.",
        "Nueva guia docs/despliegue.md: primera instalacion en servidor recien instalado, "
        "actualizaciones sin perder contenido y alta opcional de Webmin/Portainer.",
        "Solo despliegue: sin cambios de backend, API, esquema ni codigo de la aplicacion.",
    ])
    pdf.section("Por que")
    pdf.body(
        "Alcanzando a Portainer por su puerto publicado (9443), recibia un Host interno; su "
        "proteccion CSRF (Portainer 2.20+) compara ese Host con el Origin del navegador y, al no "
        "coincidir, rechazaba las acciones de escritura con 'Forbidden - origin invalid' (no se "
        "podian reiniciar/parar contenedores). Ademas el doble TLS lo hacia lento. Hablandole por "
        "la red interna con el Host publico forzado, la comprobacion cuadra y va mas rapido."
    )

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE I - MANUAL TECNICO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("1", "Cambios")
    pdf.kv_table([
        ("caddy/Caddyfile", "Bloque PORTAINER -> portainer:9000 + header_up Host/X-Forwarded-*. Webmin sigue por host.docker.internal:10000."),
        ("connect-portainer.sh", "Conecta el contenedor portainer a la red del stack (idempotente)."),
        ("docs/despliegue.md", "Guia de despliegue: primera instalacion, actualizacion y paneles."),
        (".env.example / compose", "Comentarios actualizados (Portainer por red interna, Webmin por host)."),
    ])

    pdf.chapter_title("2", "Como funciona el proxy de Portainer")
    pdf.body(
        "Portainer corre como contenedor externo a este docker-compose, asi que su red no se puede "
        "declarar aqui. connect-portainer.sh detecta la red de Caddy y conecta a ella el contenedor "
        "'portainer'. Con ambos en la misma red, Caddy resuelve 'portainer' por DNS interno de "
        "Docker y le habla por HTTP en el 9000, reenviando el Host publico. La CSRF de Portainer ve "
        "Host == Origin y permite las acciones. Repetir el script tras recrear Portainer o un "
        "docker compose down (recrean la red)."
    )

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    pdf.chapter_title("3", "Primera instalacion en un servidor recien instalado")
    pdf.code(
        "sudo mkdir -p /opt/portal-educacion && cd /opt/portal-educacion\n"
        "unzip -oq plataforma-educativa-v0.21.6.zip\n"
        "cp -rf plataforma-educativa-v0.21.6/. .\n"
        "cp .env.example .env      # dominios, ACME_EMAIL, SECRET_KEY, admin\n"
        "docker compose up -d --build\n"
        "\n"
        "# (opcional) Portainer detras del proxy, una vez:\n"
        "./connect-portainer.sh && docker compose restart caddy"
    )
    pdf.body(
        "Requisitos: Docker + Compose v2, registros DNS A de los dominios apuntando al servidor y "
        "puertos 80/443 abiertos. Caddy emite los certificados al primer acceso. El backend aplica "
        "las migraciones y crea el admin inicial si la BD esta vacia."
    )

    pdf.chapter_title("4", "Webmin tras el proxy (ajuste unico en el host)")
    pdf.code(
        "# /etc/webmin/miniserv.conf -> redirect_ssl=1\n"
        "# /etc/webmin/config        -> referers=webmin.tudominio.com host.docker.internal\n"
        "systemctl restart webmin"
    )
    pdf.body(
        "Sin esto, Webmin tras el proxy avisa de 'Trusted Referrers' y obliga a recargar (genera "
        "redirecciones al host interno). Detalle y bloque copy-paste en docs/despliegue.md."
    )

    pdf.chapter_title("5", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.21.6)", "Proxy de Portainer por red interna + script + guia de despliegue."),
        ("Hecho (V-0.21.5)", "Proxy inverso opcional Webmin/Portainer via Caddy."),
        ("Hecho (V-0.21.4)", "Tabla de contenidos: columnas de taxonomia, orden y paginacion."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.21.6.pdf")
    build_pdf(output)
