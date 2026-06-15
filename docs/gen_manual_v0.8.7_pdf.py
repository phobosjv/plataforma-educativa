# -*- coding: utf-8 -*-
"""Genera docs/manual-v0.8.7.pdf usando fpdf2."""
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


class ManualPDF(FPDF):

    def header(self) -> None:
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*INDIGO)
        self.cell(0, 8, "Plataforma Educativa - Manual Tecnico y de Usuario  V-0.8.7", align="L")
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
        self.cell(0, 10, "Manual Tecnico y de Usuario - V-0.8.7", align="C",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*BLACK)
        self.set_y(88)
        self.set_font("Helvetica", "", 11)
        self.set_fill_color(*GRAY_BG)
        self.set_x(MARGIN)
        self.multi_cell(
            INNER_W, 6,
            "Este documento describe la arquitectura, endpoints de la API, modelo de datos, "
            "guia de instalacion y manual de uso de la Plataforma Educativa V-0.8.7. "
            "Esta version corrige que el sandbox cacheaba las respuestas de error (403/404) como "
            "inmutables durante 1 año: el navegador seguia mostrando el error tras corregir el "
            "fichero. El Cache-Control ahora se aplica sin 'always' (solo a respuestas correctas).",
            border=0, fill=True,
        )
        self.ln(5)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Fecha: 2026-06-14", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, "Version del software: V-0.8.7", align="C", new_x="LMARGIN", new_y="NEXT")
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

    # ---- NOVEDADES V-0.8.7 ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 10, "NOVEDADES DE V-0.8.7", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)
    pdf.chapter_title("0", "Cambios de esta version")
    pdf.section("Corregido: el sandbox cacheaba los errores 1 año")
    pdf.bullet([
        "Sintoma: tras corregir un ejercicio que daba 403, el navegador seguia mostrando el 403 sin "
        "reintentar (no aparecia ninguna peticion en el log del sandbox).",
        "Causa: el Cache-Control 'public, max-age=31536000, immutable' se enviaba con 'always', "
        "asi que tambien cacheaba el 403/404 como inmutable.",
        "Solucion: ese Cache-Control se aplica SIN 'always' (solo a respuestas 2xx/3xx) en "
        "nginx/sandbox.conf.template y nginx/sandbox.conf. El sandbox Python ya solo lo ponia en 200.",
    ])
    pdf.section("Como aplicarlo")
    pdf.bullet([
        "Actualizar la plantilla en el servidor y: docker compose restart sandbox (re-renderiza).",
        "Vaciar la cache del navegador (incognito o recarga forzada) para soltar un error ya cacheado.",
    ])

    # ---- PARTE I: MANUAL TECNICO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE I - MANUAL TECNICO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    # 1. Descripcion del sistema
    pdf.chapter_title("1", "Descripcion del sistema")
    pdf.body(
        "Plataforma web educativa tipo CMS para alojar y ejecutar ejercicios interactivos "
        "(HTML/CSS/JS autocontenidos) y articulos de texto, dirigidos a alumnado de infantil "
        "y primaria en Espana. Acceso publico sin cuentas de alumno. Dos roles privilegiados: "
        "admin (configuracion + contenidos) y editor (gestion de contenidos)."
    )
    pdf.section("Caracteristicas principales")
    pdf.bullet([
        "Contexto configuration: paletas de color configurables desde el panel admin.",
        "Frontend React MVP completo: catalogo, login, panel admin con todas las secciones.",
        "CRUD de taxonomias (ciclos, cursos, asignaturas) con edicion inline en el frontend.",
        "Script seed_admin y entrypoint Docker con auto-creacion del admin inicial.",
        "Sistema de diseno CSS con variables custom (--cms-color-*) y clases prefijadas cms-.",
        "Paletas predefinidas infantiles aplicables en tiempo real sin recargar la pagina.",
        "Paletas personalizadas con color pickers y preview en vivo.",
        "Ajustes generales: nombre del sitio editable y seleccion de fuente de letra.",
        "Fuentes self-hosted (Nunito, Quicksand, Lexend, Atkinson Hyperlegible, Andika).",
        "Creacion/edicion de articulos de texto con editor WYSIWYG (Tiptap) y HTML saneado.",
        "Fondos/estampados tematicos (Aula, Naturaleza, Espacio, Oceano, Geometrico, Granja).",
    ])

    # 2. Arquitectura
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
        ("taxonomy", "Ciclos, cursos y asignaturas configurables (catalogos)"),
        ("configuration", "Configuracion del sitio: paleta activa, paletas personalizadas"),
    ])
    pdf.section("Regla de dependencia")
    pdf.body(
        "infrastructure -> application -> domain. "
        "El dominio no importa FastAPI, SQLAlchemy ni Pydantic de request. Jamas. "
        "Comunicacion entre contextos solo via casos de uso o eventos de dominio."
    )
    pdf.section("Patron singleton de configuracion (corregido en V-0.8.0)")
    pdf.body(
        "site_config es una unica fila con id fijo. El repositorio implementa get-or-create de "
        "forma idempotente: _get_or_create_model() consulta la fila y, si no existe, la crea y "
        "ejecuta flush() para registrarla en el identity map de SQLAlchemy. Asi, dentro del mismo "
        "caso de uso, get() y save() operan sobre la misma instancia y nunca se intenta un doble "
        "INSERT con la misma clave primaria."
    )

    # 3. Estructura de carpetas
    pdf.chapter_title("3", "Estructura de carpetas")
    pdf.code(
        "backend/app/\n"
        "  contexts/\n"
        "    identity/{domain,application,infrastructure,api}/\n"
        "    content/{domain,application,infrastructure,api}/\n"
        "    taxonomy/{domain,application,infrastructure,api}/\n"
        "    configuration/{domain,application,infrastructure,api}/\n"
        "  shared/{domain,application,infrastructure}/\n"
        "  bootstrap.py   main.py   config.py\n\n"
        "frontend/src/\n"
        "  app/{auth/,config/,App.tsx}\n"
        "  pages/{CatalogoPage,ContenidoPage,LoginPage,...}\n"
        "  pages/admin/{DashboardPage,ContenidosPage,TaxonomiaPage,\n"
        "               UsuariosPage,ConfiguracionPage}\n"
        "  shared/{api/{client.ts,schema.d.ts},ui/{PublicLayout,AdminLayout}}\n"
        "  styles/tokens.css"
    )

    # 4. Instalacion y despliegue
    pdf.chapter_title("4", "Instalacion y despliegue")
    pdf.section("Requisitos")
    pdf.bullet([
        "Docker 24+ y Docker Compose v2",
        "Puertos publicados accesibles: frontend 5173, api 5070, sandbox 5071",
        "IP o dominio del servidor alcanzable desde el navegador (para cargar el sandbox)",
    ])
    pdf.section("Arranque rapido con Docker (servidor de pruebas)")
    pdf.code(
        "# 1. Descomprimir\n"
        "unzip plataforma-educativa-v0.8.3.zip && cd plataforma-educativa-v0.8.3\n\n"
        "# 2. Configurar variables de entorno (.env en la raiz)\n"
        "cp .env.example .env\n"
        "# Editar: sustituir TU_SERVIDOR por la IP/dominio real y poner SECRET_KEY:\n"
        "#   SANDBOX_BASE_URL=http://TU_SERVIDOR:5071\n"
        "#   APP_ORIGINS=http://TU_SERVIDOR:5173\n"
        "#   CORS_ALLOW_ORIGINS=http://TU_SERVIDOR:5173\n\n"
        "# 3. Levantar (construye las imagenes)\n"
        "docker compose up -d --build\n\n"
        "# Web: http://TU_SERVIDOR:5173  |  Swagger: http://TU_SERVIDOR:5070/docs\n"
        "# El entrypoint del api ejecuta: alembic upgrade head + crea admin si no hay usuarios"
    )
    pdf.section("Variables de entorno (backend/.env)")
    pdf.kv_table([
        ("DATABASE_URL", "sqlite:///./data/db.sqlite3"),
        ("SECRET_KEY", "OBLIGATORIO cambiar en produccion (min 32 chars)"),
        ("ACCESS_TOKEN_EXPIRE_MINUTES", "60 (por defecto)"),
        ("DEFAULT_ADMIN_EMAIL", "admin@plataforma.local"),
        ("DEFAULT_ADMIN_PASSWORD", "CambiaMe1234 - CAMBIAR antes de desplegar"),
        ("HTML_STORAGE_PATH", "./data/html_files"),
        ("CORS_ORIGINS", "http://localhost:5173"),
    ])
    pdf.section("Arranque en desarrollo local")
    pdf.code(
        "# Backend (Python 3.12+)\n"
        "cd backend && python -m venv venv\n"
        "source venv/bin/activate\n"
        "pip install -r requirements.txt\n"
        "cp .env.example .env\n"
        "python -m alembic upgrade head\n"
        "uvicorn app.main:app --reload --port 8001\n\n"
        "# Frontend (Node.js 20+)\n"
        "cd frontend && npm install\n"
        "npm run dev   # -> http://localhost:5173 (proxy /api -> :8001)"
    )
    pdf.section("Crear primer admin manualmente")
    pdf.code(
        "cd backend\n"
        "python scripts/seed_admin.py admin@midominio.com MiPassword123"
    )

    # 5. API REST
    pdf.chapter_title("5", "Referencia de la API REST")
    pdf.body("Base URL: http://localhost:8001/api/v1  |  Formato: JSON  |  Auth: Bearer JWT")

    pdf.section("Autenticacion")
    pdf.endpoint_table([
        ("POST", "/auth/token", "-", "Login. Form: username + password. Devuelve JWT."),
    ])

    pdf.section("Usuarios (/users/)")
    pdf.endpoint_table([
        ("GET", "/users/", "admin", "Listar todos los usuarios"),
        ("POST", "/users/", "admin", "Crear usuario (email, password, nombre, rol)"),
    ])

    pdf.section("Contenidos (/contenidos/)")
    pdf.endpoint_table([
        ("GET", "/contenidos/", "-", "Listar contenidos publicados (catalogo publico)"),
        ("GET", "/contenidos/{id}", "-", "Obtener contenido por ID"),
        ("POST", "/contenidos/", "editor+", "Crear contenido (sanea body_html de texto)"),
        ("PUT", "/contenidos/{id}", "editor+", "Actualizar (re-sanea body_html de texto)"),
        ("POST", "/contenidos/{id}/html", "editor+", "Subir HTML de ejercicio (multipart)"),
        ("DELETE", "/contenidos/{id}/purgar", "admin", "Eliminar definitivamente (desde papelera)"),
        ("POST", "/media/imagenes", "editor+", "Subir imagen de articulo (multipart, raster)"),
        ("POST", "/contenidos/{id}/publicar", "editor+", "Publicar"),
        ("DELETE", "/contenidos/{id}", "editor+", "Mover a papelera (soft-delete)"),
        ("POST", "/contenidos/{id}/restaurar", "editor+", "Restaurar desde papelera"),
        ("GET", "/admin/contenidos/", "admin", "Listar todos (incluye papelera)"),
    ])

    pdf.section("Taxonomia (/taxonomy/)")
    pdf.endpoint_table([
        ("GET", "/taxonomy/ciclos", "-", "Listar ciclos"),
        ("POST", "/taxonomy/ciclos", "admin", "Crear ciclo"),
        ("PUT", "/taxonomy/ciclos/{id}", "admin", "Actualizar ciclo"),
        ("DELETE", "/taxonomy/ciclos/{id}", "admin", "Eliminar ciclo"),
        ("GET", "/taxonomy/cursos", "-", "Listar cursos (filtrar: ?ciclo_id=...)"),
        ("POST", "/taxonomy/cursos", "admin", "Crear curso"),
        ("PUT", "/taxonomy/cursos/{id}", "admin", "Actualizar curso"),
        ("DELETE", "/taxonomy/cursos/{id}", "admin", "Eliminar curso"),
        ("GET", "/taxonomy/asignaturas", "-", "Listar asignaturas"),
        ("POST", "/taxonomy/asignaturas", "admin", "Crear asignatura (+ color opcional)"),
        ("PUT", "/taxonomy/asignaturas/{id}", "admin", "Actualizar asignatura"),
        ("DELETE", "/taxonomy/asignaturas/{id}", "admin", "Eliminar asignatura"),
    ])

    pdf.section("Configuracion del sitio (/config/)")
    pdf.endpoint_table([
        ("GET", "/config/", "-", "Obtener config: nombre, fuente, fondo, paleta, paletas"),
        ("PUT", "/config/general", "admin", "Cambiar nombre del sitio y fuente de letra"),
        ("PUT", "/config/paleta", "admin", "Activar paleta (predefinida o personalizada)"),
        ("POST", "/config/paletas", "admin", "Crear paleta personalizada"),
        ("PUT", "/config/paletas/{id}", "admin", "Actualizar paleta personalizada"),
        ("DELETE", "/config/paletas/{id}", "admin", "Eliminar paleta personalizada"),
    ])
    pdf.body(
        "Nota V-0.8.0: estos endpoints crean la fila singleton de configuracion de forma "
        "idempotente. La primera escritura sobre una BD sin configuracion previa ya NO produce 500."
    )

    pdf.section("Origen sandbox (servidor aparte: :8002 dev / sandbox.<dominio> prod)")
    pdf.endpoint_table([
        ("GET", "/ejercicio/{hash}", "-", "Sirve el HTML del ejercicio con CSP estricta"),
        ("GET", "/health", "-", "Readiness del servidor sandbox"),
    ])

    pdf.section("Paletas predefinidas disponibles")
    pdf.kv_table([
        ("cielo", "Cielo Azul - tonos azules claros"),
        ("bosque", "Bosque Magico - tonos verdes naturales"),
        ("coral", "Coral Feliz - tonos rosas y rojos suaves"),
        ("sol", "Sol Brillante - tonos amarillos y naranjas"),
        ("lavanda", "Lavanda Sonadora - tonos morados suaves"),
        ("estandar", "Estandar - neutros, sin color fuerte"),
    ])

    # 6. Modelo de datos
    pdf.chapter_title("6", "Modelo de datos")
    pdf.section("Tabla: user")
    pdf.kv_table([
        ("id", "UUID (str) PK"),
        ("email", "VARCHAR(255) UNIQUE NOT NULL"),
        ("nombre", "VARCHAR(255)"),
        ("hashed_password", "VARCHAR(255) - Argon2id"),
        ("rol", "VARCHAR(50) - 'admin' | 'editor'"),
        ("activo", "BOOLEAN"),
        ("creado_en", "DATETIME"),
    ])
    pdf.section("Tabla: content")
    pdf.kv_table([
        ("id", "UUID (str) PK"),
        ("titulo", "VARCHAR(500)"),
        ("tipo", "VARCHAR(50) - 'interactivo' | 'texto'"),
        ("estado", "VARCHAR(50) - borrador|publicado|archivado|papelera"),
        ("ciclo_id / curso_id / asignatura_id", "UUID FK nullable"),
        ("hash_html", "VARCHAR(64) nullable - SHA-256 del HTML interactivo (servido en sandbox)"),
        ("body_html", "TEXT nullable - HTML sanitizado (tipo=texto)"),
        ("creado_en / actualizado_en", "DATETIME"),
    ])
    pdf.section("Tabla: ciclo / curso / asignatura")
    pdf.kv_table([
        ("id", "UUID (str) PK"),
        ("nombre", "VARCHAR(255) UNIQUE (ciclo/asignatura)"),
        ("orden", "INTEGER"),
        ("ciclo_id", "UUID FK - solo en tabla curso"),
        ("color", "VARCHAR(7) nullable - solo en tabla asignatura"),
    ])
    pdf.section("Tabla: site_config (singleton)")
    pdf.kv_table([
        ("id", "VARCHAR(36) PK fijo - '00000000-0000-0000-0000-000000000001'"),
        ("nombre_sitio", "VARCHAR(255) - nombre visible del sitio"),
        ("paleta_activa", "VARCHAR(100) - ID de la paleta activa"),
        ("paletas_json", "TEXT - JSON array con paletas personalizadas"),
        ("fuente_activa", "VARCHAR(100) - ID de la fuente activa (default 'sistema')"),
        ("fondo_activo", "VARCHAR(100) - ID del fondo/estampado (default 'ninguno')"),
    ])

    # 7. Seguridad
    pdf.chapter_title("7", "Seguridad")
    pdf.section("Autenticacion y autorizacion")
    pdf.bullet([
        "Contrasenas con Argon2id. Minimo 8 caracteres.",
        "JWT HS256 firmado con SECRET_KEY. Expiracion configurable.",
        "Roles: admin (completo) y editor (solo contenidos).",
        "Endpoints de lectura publica sin autenticacion.",
    ])
    pdf.section("Aislamiento del sandbox (ejercicios interactivos)")
    pdf.bullet([
        "iframe sandbox='allow-scripts' (SIN allow-same-origin).",
        "Servidos desde un origen distinto (sandbox.<dominio> prod, :8002 dev) con CSP estricta.",
        "El JS del ejercicio no accede a cookies ni localStorage del origen principal.",
        "Nunca se renderiza HTML de ejercicio en el origen de la app.",
    ])
    pdf.section("Sanitizacion asimetrica")
    pdf.bullet([
        "HTML de articulos (tipo=texto): SIEMPRE sanitizado en servidor (Bleach).",
        "HTML de ejercicios (tipo=interactivo): NO sanitizado (debe ejecutar JS).",
        "HTML de ejercicios servido aislado: el sandbox y la CSP sustituyen a la sanitizacion.",
    ])
    pdf.section("Privacidad y proteccion de menores")
    pdf.bullet([
        "Sin cuentas de alumno, sin cookies de seguimiento, sin perfilado.",
        "Visitas anonimas y agregadas. Sin publicidad dirigida a menores (DSA art. 28).",
        "Datos minimos: solo email y contrasena para usuarios con rol.",
    ])

    # 8. Tests
    pdf.chapter_title("8", "Tests")
    pdf.kv_table([
        ("Unitarios (dominio + handlers)", "mocks de repositorios, sin BD"),
        ("Integracion (endpoints)", "SQLite en memoria, TestClient FastAPI"),
        ("Regresion configuration", "fixture con autoflush=False (igual a produccion)"),
        ("Total", "111 tests - todos pasan en V-0.8.0"),
    ])
    pdf.code(
        "cd backend\n"
        "pytest -v                        # todos\n"
        "pytest -v tests/unit/            # solo unitarios\n"
        "pytest -v tests/integration/     # solo integracion\n"
        "pytest --cov=app --cov-report=html  # cobertura"
    )

    # ---- PARTE II: MANUAL DE USUARIO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    # 9. Acceso publico
    pdf.chapter_title("9", "Acceso publico - Catalogo")
    pdf.body(
        "La portada del sitio muestra el catalogo de contenidos publicados. No es necesario "
        "registrarse ni hacer login. Los visitantes pueden navegar por el catalogo, abrir "
        "ejercicios interactivos (en iframe aislado) y leer articulos de texto."
    )
    pdf.section("Tipos de contenido")
    pdf.kv_table([
        ("Ejercicio interactivo", "HTML/CSS/JS autocontenido en iframe sandbox servido desde un "
         "origen aislado. Sin acceso al origen de la app. Seguro para menores."),
        ("Articulo de texto", "HTML enriquecido sanitizado. "
         "Imagenes, listas, tablas y formato de texto permitidos."),
    ])

    # 10. Login
    pdf.chapter_title("10", "Login al panel de administracion")
    pdf.body(
        "Pulsar 'Acceder' en la barra de navegacion publica. "
        "Introducir email y contrasena. Tras el login, el sistema redirige automaticamente "
        "al Panel Admin (/admin)."
    )
    pdf.bullet([
        "El token JWT se almacena en localStorage con clave 'auth_token'.",
        "Expiracion por defecto: 60 minutos.",
        "Para cerrar sesion: boton 'Cerrar sesion' en el sidebar del panel admin.",
    ])

    # 11. Dashboard
    pdf.chapter_title("11", "Panel admin - Inicio (Dashboard)")
    pdf.body(
        "Muestra tarjetas con estadisticas del sitio: contenidos publicados, total de "
        "usuarios y ciclos configurados. Punto de entrada al panel de gestion."
    )

    # 12. Contenidos
    pdf.chapter_title("12", "Panel admin - Contenidos")
    pdf.body(
        "Lista todos los contenidos con su estado: borrador, publicado, archivado, papelera. "
        "Filtrado y paginacion disponibles en versiones futuras."
    )
    pdf.section("Acciones disponibles")
    pdf.kv_table([
        ("Publicar", "Pone el contenido en estado 'publicado' (visible en catalogo)."),
        ("Borrar", "Mueve a la papelera (borrado logico, recuperable)."),
        ("Restaurar", "Recupera un contenido de la papelera."),
    ])
    pdf.body(
        "Crear: boton + Nuevo articulo. Se elige el tipo (texto o interactivo). En los "
        "interactivos, tras crear el contenido se sube el fichero HTML desde la edicion."
    )

    # 13. Taxonomia
    pdf.chapter_title("13", "Panel admin - Taxonomia")
    pdf.body(
        "Gestion de ciclos, cursos y asignaturas educativas del sistema espanol. "
        "Todos los catalogos son configurables; no hay valores fijos en el sistema."
    )
    pdf.section("Gestion de ciclos y cursos")
    pdf.bullet([
        "Anadir: escribir el nombre en el campo de texto y pulsar '+ Anadir'.",
        "Editar: pulsar el icono lapiz o hacer doble clic sobre el nombre. "
        "Confirmar con Enter o la marca de verificacion. Cancelar con Escape.",
        "Eliminar: pulsar el icono papelera (solicita confirmacion).",
    ])
    pdf.section("Gestion de asignaturas")
    pdf.body(
        "Mismas acciones que ciclos y cursos, con la opcion adicional de asignar "
        "un color representativo mediante un selector de color HTML."
    )

    # 14. Apariencia
    pdf.chapter_title("14", "Panel admin - Apariencia y ajustes")
    pdf.section("Ajustes generales: nombre del sitio")
    pdf.body(
        "En la seccion 'Ajustes generales', escribir el nombre deseado en el campo 'Nombre del "
        "sitio' (maximo 80 caracteres) y pulsar 'Guardar cambios'. El nombre aparece al instante "
        "en la barra publica, el pie de pagina y el sidebar de administracion."
    )
    pdf.section("Ajustes generales: fuente de letra")
    pdf.body(
        "Debajo del nombre se muestra una rejilla de fuentes, cada una previsualizada en su "
        "propia tipografia. Hacer clic en la deseada y pulsar 'Guardar cambios' para aplicarla "
        "a todo el sitio. Catalogo disponible:"
    )
    pdf.kv_table([
        ("Sistema", "Fuente nativa del dispositivo. Rapida, sin descarga."),
        ("Nunito", "Redondeada y calida. Acogedora para los mas pequenos."),
        ("Quicksand", "Geometrica y suave, con aire moderno."),
        ("Lexend", "Disenada para mejorar la fluidez de lectura."),
        ("Atkinson Hyperlegible", "Maxima legibilidad, pensada para baja vision."),
        ("Andika", "Creada para quienes aprenden a leer."),
    ])
    pdf.body(
        "Las fuentes (salvo Sistema) son self-hosted: las sirve la propia app, sin contactar con "
        "ningun servidor externo, protegiendo la privacidad de los menores."
    )
    pdf.section("Ajustes generales: fondo / estampado")
    pdf.body(
        "Rejilla con Ninguno (fondo liso) y 6 tematicas: Aula, Naturaleza, Espacio, Oceano, "
        "Geometrico y Granja. Cada opcion muestra una vista previa. Al elegir una y pulsar "
        "'Guardar cambios', el estampado se aplica a todo el sitio."
    )
    pdf.kv_table([
        ("Aula", "Pizarra, lapiz, reloj, regla."),
        ("Naturaleza", "Pino, hoja, seta, bellota."),
        ("Espacio", "Cohete, planeta, estrella, luna."),
        ("Oceano", "Pez, concha, burbujas, estrella de mar."),
        ("Geometrico", "Formas y lunares (neutro)."),
        ("Granja", "Granero, trigo, valla, sol."),
    ])
    pdf.body(
        "El estampado se recolorea con la paleta activa y se muestra a baja opacidad, detras del "
        "contenido, para no restar legibilidad. Los patrones son SVG self-hosted."
    )
    pdf.section("Activar una paleta predefinida")
    pdf.body(
        "En la seccion 'Paletas predefinidas', hacer clic en cualquier swatch de color. "
        "La paleta se activa inmediatamente en todo el sitio (publico y privado). "
        "La paleta activa muestra un badge 'Activa' y borde destacado."
    )
    pdf.section("Como funciona la paleta")
    pdf.body(
        "Cada paleta define cuatro colores base: Fondo (bg), Superficie (surface), "
        "Texto (fg) y Color principal (primary). El sistema deriva automaticamente "
        "colores secundarios (hover, muted, border) mediante calculo de opacidad y "
        "oscurecimiento. Los colores se aplican como variables CSS en :root."
    )
    pdf.section("Crear una paleta personalizada")
    pdf.bullet([
        "Pulsar el boton '+ Nueva paleta' en la seccion 'Paletas personalizadas'.",
        "Introducir un nombre descriptivo.",
        "Elegir los 4 colores con los selectores de color del navegador.",
        "Observar el preview en vivo (muestra como quedaria la superficie y el color principal).",
        "Pulsar 'Guardar'. La paleta queda disponible para activar.",
    ])
    pdf.section("Manejo de errores (mejora de V-0.8.0)")
    pdf.body(
        "Si una operacion de paleta falla (por ejemplo, crear una paleta con un ID ya existente "
        "o eliminar la paleta actualmente activa), la pagina muestra un mensaje de error claro en "
        "la parte superior en lugar de no hacer nada. Antes, estos fallos se ignoraban en silencio."
    )
    pdf.section("Eliminar una paleta personalizada")
    pdf.body(
        "Pulsar el boton 'x' en la esquina del swatch de la paleta personalizada. "
        "No es posible eliminar la paleta actualmente activa. "
        "Las paletas predefinidas no se pueden eliminar."
    )

    # 15. Usuarios
    pdf.chapter_title("15", "Panel admin - Usuarios (solo admin)")
    pdf.body(
        "Accesible unicamente para el rol 'admin'. Lista todos los usuarios del sistema."
    )
    pdf.section("Crear un nuevo usuario")
    pdf.bullet([
        "Rellenar email, nombre, contrasena y rol (admin o editor).",
        "Pulsar 'Crear usuario'.",
        "La contrasena se almacena hasheada con Argon2id; nunca en texto plano.",
        "El email debe ser unico en el sistema.",
    ])

    # 16. Roadmap
    pdf.chapter_title("16", "Roadmap")
    pdf.kv_table([
        ("Hecho (V-0.8.7)", "Fix: el sandbox cacheaba los errores 1 año (Cache-Control sin always)."),
        ("Hecho (V-0.8.6)", "Fix 403 Forbidden en ejercicios interactivos (permisos 0o644)."),
        ("Siguiente", "Logotipo del sitio configurable. Buscador full-text (FTS5) en el catalogo."),
        ("V-1.0.0", "Despliegue en VPS con Nginx + HTTPS. E2E Playwright."),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.8.7.pdf")
    build_pdf(output)
