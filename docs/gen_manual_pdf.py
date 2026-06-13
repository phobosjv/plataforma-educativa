# -*- coding: latin-1 -*-
"""Script de uso unico: genera docs/manual-v0.1.0.pdf usando fpdf."""

from __future__ import annotations

from fpdf import FPDF

PAGE_W = 210
MARGIN = 18
INNER_W = PAGE_W - 2 * MARGIN

INDIGO = (79, 70, 229)
INDIGO_LIGHT = (224, 231, 255)
GRAY_BG = (245, 247, 250)
BLACK = (30, 30, 30)
WHITE = (255, 255, 255)


class ManualPDF(FPDF):

    def header(self) -> None:
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*INDIGO)
        self.cell(0, 8, "Plataforma Educativa - Manual Tecnico y de Usuario  V-0.1.0", align="L")
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
        self.set_y(20)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(*WHITE)
        self.cell(0, 12, "Plataforma Educativa", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 14)
        self.cell(0, 8, "CMS educativo interactivo para infantil y primaria", align="C",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "B", 18)
        self.set_y(60)
        self.cell(0, 10, "Manual Tecnico y de Usuario - V-0.1.0", align="C",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*BLACK)
        self.set_y(90)
        self.set_font("Helvetica", "", 11)
        self.set_fill_color(*GRAY_BG)
        self.set_x(MARGIN)
        self.multi_cell(
            INNER_W, 6,
            "Este documento describe la arquitectura, los endpoints de la API, el modelo "
            "de datos y las instrucciones de instalacion y uso de la plataforma educativa "
            "en su version inicial (V-0.1.0). Esta dirigido tanto al equipo tecnico "
            "(administradores de sistema, desarrolladores) como a los editores de contenido.",
            border=0, fill=True,
        )
        self.ln(6)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Fecha: 2026-06-13", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, "Version del software: V-0.1.0", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, "Licencia: MIT (open source)", align="C")
        self.set_text_color(*BLACK)

    def chapter_title(self, num: str, title: str) -> None:
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
        self.set_font("Courier", "", 8.5)
        self.set_x(MARGIN)
        self.multi_cell(INNER_W, 5, text, border="1", fill=True)
        self.set_font("Helvetica", "", 10)
        self.ln(2)

    def kv_table(self, rows: list) -> None:
        col1 = 60
        col2 = INNER_W - col1
        for i, (k, v) in enumerate(rows):
            fill = i % 2 == 0
            if fill:
                self.set_fill_color(245, 247, 250)
            else:
                self.set_fill_color(255, 255, 255)
            self.set_x(MARGIN)
            self.set_font("Helvetica", "B", 9)
            self.cell(col1, 6, "  " + k, border="LTB", fill=fill)
            self.set_font("Helvetica", "", 9)
            self.multi_cell(col2, 6, "  " + v, border="RTB", fill=fill)
        self.ln(3)

    def endpoint_table(self, rows: list) -> None:
        cols = [18, 75, 28, INNER_W - 18 - 75 - 28]
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
            if fill:
                self.set_fill_color(245, 247, 250)
            else:
                self.set_fill_color(255, 255, 255)
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

    # ---- PARTE I: MANUAL TECNICO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE I - MANUAL TECNICO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    # 1. Vision general
    pdf.chapter_title("1", "Vision general del sistema")
    pdf.body(
        "La Plataforma Educativa es un CMS web disenado para publicar y ejecutar ejercicios "
        "interactivos (HTML/CSS/JS) y articulos de texto dirigidos a alumnado de infantil y primaria "
        "en Espana. El acceso al catalogo es publico, sin registro. Dos roles privilegiados - "
        "admin y editor - gestionan los contenidos desde una API REST."
    )
    pdf.section("Objetivos principales")
    pdf.bullet([
        "Publicar y ejecutar ejercicios educativos de forma segura para menores.",
        "Permitir a editores gestionar contenidos (CRUD, versionado, papelera) con baja friccion.",
        "Ofrecer a familias y alumnos descubrir contenido por catalogo y buscador.",
        "Sostenibilidad economica sin comprometer la privacidad (DSA/RGPD).",
        "Mantenibilidad por una sola persona: simplicidad por encima de la sofisticacion.",
    ])
    pdf.section("Restricciones de diseno clave")
    pdf.bullet([
        "Sin cuentas de alumno. Sin cookies de seguimiento. Visitas anonimas y agregadas.",
        "Publicidad/afiliacion solo en zonas de adultos (DSA art. 28).",
        "Ejercicios aislados en iframe sandbox desde subdominio separado.",
        "SQLite WAL como unica base de datos. Sin microservicios ni broker.",
    ])

    # 2. Arquitectura
    pdf.chapter_title("2", "Arquitectura")
    pdf.section("Estilo arquitectonico")
    pdf.body(
        "Monolito modular con Arquitectura Hexagonal (Ports & Adapters) y patrones de "
        "Clean Architecture. DDD tactico ligero con contextos acotados como modulos. "
        "CQRS solo logico (separacion lectura/escritura, sin segunda base de datos)."
    )
    pdf.section("Regla de dependencia")
    pdf.body(
        "Las dependencias siempre apuntan hacia dentro: infrastructure -> application -> domain. "
        "El dominio no conoce FastAPI, SQLAlchemy, ni Pydantic de request. Jamas."
    )
    pdf.section("Contextos acotados (V-0.1.0 implementados)")
    pdf.kv_table([
        ("identity", "Autenticacion JWT + gestion de usuarios (admin/editor)"),
        ("content", "CRUD de contenidos educativos, versionado e historial, papelera"),
    ])
    pdf.section("Contextos acotados (planificados)")
    pdf.kv_table([
        ("taxonomy", "Ciclos, cursos, asignaturas - catalogos configurables"),
        ("media", "Ficheros adjuntos (imagenes, audio)"),
        ("auditing", "Registro de auditoria de acciones"),
        ("analytics", "Conteo de visitas anonimas y agregadas"),
        ("configuration", "Nombre del sitio, logotipo, configuracion global"),
    ])

    # 3. Estructura de carpetas
    pdf.chapter_title("3", "Estructura de carpetas")
    pdf.code(
        "plataforma-educativa/\n"
        "  backend/\n"
        "    app/\n"
        "      bootstrap.py          # wiring ORM (side-effect imports)\n"
        "      config.py             # Settings via pydantic-settings\n"
        "      main.py               # FastAPI app, routers, exception handlers\n"
        "      contexts/\n"
        "        identity/\n"
        "          domain/           # model, ports, services (puro Python)\n"
        "          application/      # commands, queries, dtos, handlers\n"
        "          infrastructure/   # ORM models, repos, auth_service\n"
        "          api/              # router, schemas, dependencies\n"
        "        content/            # misma estructura\n"
        "      shared/\n"
        "        domain/base.py      # Entity, DomainError, DomainEvent\n"
        "        infrastructure/     # database.py, unit_of_work.py\n"
        "    migrations/             # Alembic\n"
        "    tests/\n"
        "      unit/\n"
        "      integration/\n"
        "    pyproject.toml\n"
        "  frontend/                 # React + TypeScript (pendiente)\n"
        "  docker-compose.yml\n"
        "  CLAUDE.md\n"
        "  CHANGELOG.md\n"
        "  docs/"
    )

    # 4. Instalacion y despliegue
    pdf.chapter_title("4", "Instalacion y despliegue")
    pdf.section("Requisitos del servidor")
    pdf.bullet([
        "Docker Engine 24+ y Docker Compose v2",
        "Puerto 8000 accesible (o 80/443 con proxy inverso Nginx/Caddy)",
        "Subdominio sandbox.<dominio> apuntando al mismo servidor (ejercicios interactivos)",
        "Al menos 512 MB RAM, 1 vCPU",
    ])
    pdf.section("Despliegue rapido con Docker Compose")
    pdf.code(
        "# 1. Descomprimir el zip de distribucion\n"
        "unzip plataforma-educativa-v0.1.0.zip\n"
        "cd plataforma-educativa-v0.1.0\n\n"
        "# 2. Copiar y configurar variables de entorno\n"
        "cp .env.example .env\n"
        "nano .env   # editar SECRET_KEY y demas valores\n\n"
        "# 3. Levantar servicios\n"
        "docker compose up -d\n\n"
        "# 4. Ejecutar migraciones\n"
        "docker compose exec backend alembic upgrade head\n\n"
        "# 5. Verificar\n"
        "curl http://localhost:8000/health\n"
        "# -> {\"status\": \"ok\"}"
    )
    pdf.section("Variables de entorno")
    pdf.kv_table([
        ("DATABASE_URL", "sqlite:///./data/plataforma.db (por defecto)"),
        ("SECRET_KEY", "Clave secreta para JWT - OBLIGATORIO cambiar en produccion"),
        ("ACCESS_TOKEN_EXPIRE_MINUTES", "Duracion del token JWT (default: 60)"),
        ("MEDIA_BASE_DIR", "Ruta base para almacenamiento de ficheros HTML (default: ./media)"),
        ("ALLOWED_ORIGINS", "Origenes CORS permitidos (default: http://localhost:5173)"),
        ("ENVIRONMENT", "development | production"),
    ])
    pdf.section("Crear el primer usuario administrador")
    pdf.body(
        "En V-0.1.0 no existe interfaz de administracion web. El primer usuario admin se crea "
        "llamando directamente al endpoint POST /api/v1/users/. Para arrancar el sistema desde "
        "cero use el script de semilla incluido:"
    )
    pdf.code(
        "docker compose exec backend python -m app.scripts.seed_admin \\\n"
        "  --email admin@ejemplo.com --password TuPasswordSegura123"
    )

    # 5. API
    pdf.chapter_title("5", "Referencia de la API (V-0.1.0)")
    pdf.body(
        "La API sigue principios REST con prefijo /api/v1. "
        "La autenticacion utiliza el flujo OAuth2 Password Bearer (JWT HS256). "
        "Los errores devuelven JSON con campo 'detail' y codigo HTTP estandar."
    )
    pdf.section("Contexto identity - Autenticacion y usuarios")
    pdf.endpoint_table([
        ("POST", "/api/v1/auth/token", "-", "Obtener token JWT (form: username + password)"),
        ("GET", "/api/v1/users/", "admin", "Listar todos los usuarios"),
        ("POST", "/api/v1/users/", "admin", "Crear nuevo usuario (admin o editor)"),
    ])
    pdf.section("Contexto content - Catalogo publico (sin autenticacion)")
    pdf.endpoint_table([
        ("GET", "/api/v1/contenidos/", "-", "Listar contenidos publicados"),
        ("GET", "/api/v1/contenidos/{id}", "-", "Obtener contenido por ID"),
    ])
    pdf.section("Contexto content - Gestion de contenidos (editor+)")
    pdf.endpoint_table([
        ("POST", "/api/v1/contenidos/", "editor", "Crear nuevo contenido (borrador)"),
        ("PUT", "/api/v1/contenidos/{id}", "editor", "Actualizar titulo, descripcion, cuerpo"),
        ("POST", "/api/v1/contenidos/{id}/publicar", "editor", "Publicar contenido"),
        ("POST", "/api/v1/contenidos/{id}/archivar", "editor", "Retirar de publicacion"),
        ("DELETE", "/api/v1/contenidos/{id}", "editor", "Mover a papelera (soft-delete)"),
        ("POST", "/api/v1/contenidos/{id}/restaurar", "editor", "Restaurar desde papelera"),
    ])
    pdf.section("Contexto content - Panel admin")
    pdf.endpoint_table([
        ("GET", "/api/v1/admin/contenidos/", "admin", "Listar todos los contenidos (incl. papelera)"),
        ("GET", "/api/v1/admin/contenidos/papelera", "admin", "Listar solo papelera"),
        ("DELETE", "/api/v1/admin/contenidos/{id}/purgar", "admin", "Borrado permanente"),
    ])

    # 6. Modelo de datos
    pdf.chapter_title("6", "Modelo de datos")
    pdf.section("Tabla: user")
    pdf.kv_table([
        ("id", "TEXT PK - UUID en formato string"),
        ("email", "TEXT UNIQUE NOT NULL"),
        ("password_hash", "TEXT NOT NULL - hash Argon2id"),
        ("role", "TEXT NOT NULL - 'admin' | 'editor'"),
        ("is_active", "INTEGER NOT NULL - 1=activo, 0=inactivo"),
        ("created_at", "TEXT NOT NULL - ISO 8601 UTC"),
    ])
    pdf.section("Tabla: content")
    pdf.kv_table([
        ("id", "TEXT PK - UUID"),
        ("tipo", "TEXT NOT NULL - 'interactivo' | 'texto'"),
        ("titulo", "TEXT NOT NULL"),
        ("descripcion", "TEXT"),
        ("autor_id", "TEXT FK -> user.id"),
        ("ciclo_id / curso_id / asignatura_id", "TEXT - IDs de taxonomia (nullable)"),
        ("idioma", "TEXT DEFAULT 'es'"),
        ("tags_json", "TEXT - JSON array de etiquetas"),
        ("is_published", "INTEGER - 1=publicado"),
        ("is_deleted", "INTEGER - 1=en papelera (soft delete)"),
        ("body_html", "TEXT - cuerpo HTML (tipo=texto; sanitizado)"),
        ("hash_html", "TEXT - SHA-256 del fichero HTML (tipo=interactivo)"),
        ("created_at / updated_at", "TEXT - ISO 8601 UTC"),
    ])
    pdf.section("Tabla: content_version (historial inmutable)")
    pdf.kv_table([
        ("id", "TEXT PK - UUID"),
        ("content_id", "TEXT FK -> content.id"),
        ("version_no", "INTEGER - numero correlativo (1, 2, 3...)"),
        ("metadata_snapshot_json", "TEXT - JSON con titulo, descripcion, etiquetas, tipo, idioma"),
        ("body_html", "TEXT - cuerpo en este momento"),
        ("hash_html", "TEXT - hash del HTML interactivo"),
        ("created_by", "TEXT FK -> user.id"),
        ("created_at", "TEXT - ISO 8601 UTC"),
    ])
    pdf.body(
        "Restriccion UNIQUE (content_id, version_no) garantiza unicidad del historial. "
        "Las versiones nunca se borran; restaurar un contenido no destruye versiones anteriores."
    )

    # 7. Seguridad
    pdf.chapter_title("7", "Modelo de seguridad")
    pdf.section("Autenticacion y autorizacion")
    pdf.bullet([
        "Contrasenas hasheadas con Argon2id (parametros por defecto de argon2-cffi).",
        "JWT HS256 firmado con SECRET_KEY. Expiracion configurable (default 60 min).",
        "Roles: admin (gestion completa + usuarios) y editor (solo contenidos).",
        "Endpoints de lectura publica sin autenticacion.",
    ])
    pdf.section("Aislamiento del sandbox (ejercicios interactivos)")
    pdf.body(
        "Los ejercicios HTML/JS nunca se sirven desde el origen de la aplicacion. "
        "Se sirven exclusivamente desde sandbox.<dominio> con:"
    )
    pdf.bullet([
        "iframe con atributo sandbox='allow-scripts' (sin allow-same-origin).",
        "CSP estricta en las cabeceras del subdominio sandbox.",
        "El JS del ejercicio no puede acceder a cookies ni localStorage del origen principal.",
    ])
    pdf.section("Sanitizacion asimetrica")
    pdf.bullet([
        "HTML de articulos (tipo=texto): SIEMPRE sanitizado en servidor y cliente.",
        "HTML de ejercicios (tipo=interactivo): NUNCA sanitizado (debe ejecutar JS). "
        "Por eso se sirven aislados.",
    ])
    pdf.section("Privacidad y menores")
    pdf.bullet([
        "Sin cuentas de alumno. Sin perfilado. Sin cookies de seguimiento.",
        "Visitas contadas de forma anonima y agregada (en batches, no por peticion).",
        "Publicidad/afiliacion prohibida en zonas de contenido para menores (DSA art. 28).",
    ])

    # 8. Tests
    pdf.chapter_title("8", "Tests (V-0.1.0)")
    pdf.kv_table([
        ("Tests unitarios", "27 tests - dominio identity + content, handlers con MagicMock"),
        ("Tests de integracion", "19 tests - endpoints REST con SQLite en memoria (StaticPool)"),
        ("Total", "46 tests - todos pasan en V-0.1.0"),
    ])
    pdf.section("Ejecutar los tests")
    pdf.code(
        "cd backend\n"
        "pip install -e '.[dev]'\n"
        "pytest                    # todos los tests\n"
        "pytest -v tests/unit/     # solo unitarios\n"
        "pytest -v tests/integration/  # solo integracion\n"
        "ruff check .              # linting\n"
        "black --check .           # formato\n"
        "mypy app                  # tipos"
    )

    # ---- PARTE II: MANUAL DE USUARIO ----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "PARTE II - MANUAL DE USUARIO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*BLACK)
    pdf.ln(4)

    # 9. Primeros pasos
    pdf.chapter_title("9", "Primeros pasos para el editor")
    pdf.section("Obtener un token de acceso")
    pdf.body(
        "Toda operacion de gestion requiere un token JWT. Para obtenerlo, envia una "
        "peticion al endpoint de autenticacion con tu email y contrasena:"
    )
    pdf.code(
        "curl -X POST http://tu-dominio.com/api/v1/auth/token \\\n"
        "  -d 'username=editor@ejemplo.com&password=TuPassword' \\\n"
        "  -H 'Content-Type: application/x-www-form-urlencoded'\n\n"
        "# Respuesta:\n"
        '# {"access_token": "eyJ...", "token_type": "bearer"}'
    )
    pdf.body(
        "Guarda el valor de access_token. Incluyelo en la cabecera Authorization de "
        "todas las peticiones de gestion:"
    )
    pdf.code("Authorization: Bearer eyJ...")

    # 10. Gestion de contenidos
    pdf.chapter_title("10", "Gestion de contenidos")
    pdf.section("Crear un contenido (borrador)")
    pdf.body("Un contenido nuevo se crea siempre como borrador (no publicado).")
    pdf.code(
        'curl -X POST http://tu-dominio.com/api/v1/contenidos/ \\\n'
        '  -H "Authorization: Bearer $TOKEN" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{\n'
        '    "titulo": "Las vocales",\n'
        '    "descripcion": "Ejercicio interactivo para repasar las vocales",\n'
        '    "tipo": "interactivo",\n'
        '    "idioma": "es",\n'
        '    "etiquetas": ["lengua", "vocales"],\n'
        '    "body_html": null\n'
        '  }\''
    )
    pdf.section("Tipos de contenido")
    pdf.kv_table([
        ("interactivo",
         "Ejercicio HTML/CSS/JS autocontenido. Se ejecuta en el cliente, aislado en iframe. "
         "El campo body_html es null; el HTML se sube como fichero y se referencia por hash SHA-256."),
        ("texto",
         "Articulo o recurso en HTML enriquecido. El contenido va en el campo body_html "
         "y siempre se sanitiza antes de almacenarse y mostrarse."),
    ])
    pdf.section("Ciclo de vida de un contenido")
    pdf.bullet([
        "BORRADOR - recien creado. Visible solo para editores y admins.",
        "PUBLICADO - visible en el catalogo publico. POST .../{id}/publicar",
        "ARCHIVADO - retirado del catalogo sin borrar. POST .../{id}/archivar",
        "PAPELERA - borrado logico. Solo visible en el panel admin. DELETE .../{id}",
        "RESTAURADO - recuperado de la papelera. POST .../{id}/restaurar",
    ])
    pdf.section("Publicar un contenido")
    pdf.code(
        "curl -X POST http://tu-dominio.com/api/v1/contenidos/{id}/publicar \\\n"
        '  -H "Authorization: Bearer $TOKEN"'
    )
    pdf.section("Archivar (retirar de publicacion)")
    pdf.code(
        "curl -X POST http://tu-dominio.com/api/v1/contenidos/{id}/archivar \\\n"
        '  -H "Authorization: Bearer $TOKEN"'
    )
    pdf.section("Mover a la papelera (soft-delete)")
    pdf.code(
        "curl -X DELETE http://tu-dominio.com/api/v1/contenidos/{id} \\\n"
        '  -H "Authorization: Bearer $TOKEN"'
    )
    pdf.section("Restaurar desde la papelera")
    pdf.code(
        "curl -X POST http://tu-dominio.com/api/v1/contenidos/{id}/restaurar \\\n"
        '  -H "Authorization: Bearer $TOKEN"'
    )
    pdf.section("Historial de versiones")
    pdf.body(
        "Cada vez que se modifica un contenido se crea automaticamente una version "
        "inmutable. Las versiones registran titulo, descripcion, etiquetas, idioma, "
        "tipo, cuerpo HTML y hash del fichero interactivo en el momento del cambio. "
        "Las versiones nunca se borran y restaurar no destruye el historial."
    )

    # 11. Gestion de usuarios (admin)
    pdf.chapter_title("11", "Gestion de usuarios (solo admin)")
    pdf.section("Listar usuarios")
    pdf.code(
        "curl http://tu-dominio.com/api/v1/users/ \\\n"
        '  -H "Authorization: Bearer $ADMIN_TOKEN"'
    )
    pdf.section("Crear un nuevo usuario")
    pdf.code(
        'curl -X POST http://tu-dominio.com/api/v1/users/ \\\n'
        '  -H "Authorization: Bearer $ADMIN_TOKEN" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{"email": "editor@ejemplo.com", "password": "Pass1234!", "rol": "editor"}\''
    )
    pdf.bullet([
        "rol puede ser 'admin' o 'editor'.",
        "El email debe ser unico en el sistema.",
        "La contrasena se hashea con Argon2id; nunca se almacena en texto plano.",
    ])

    # 12. Catalogo publico
    pdf.chapter_title("12", "Catalogo publico (sin autenticacion)")
    pdf.body(
        "Cualquier visitante puede consultar el catalogo y ver los contenidos publicados "
        "sin necesidad de autenticarse ni registrarse."
    )
    pdf.section("Listar contenidos publicados")
    pdf.code("curl http://tu-dominio.com/api/v1/contenidos/")
    pdf.section("Obtener un contenido especifico")
    pdf.code("curl http://tu-dominio.com/api/v1/contenidos/{id}")
    pdf.body(
        "La respuesta incluye titulo, descripcion, tipo, idioma, etiquetas y, "
        "para tipo=texto, el HTML del cuerpo. Para tipo=interactivo, la respuesta "
        "incluye la URL del iframe sandbox que el navegador puede mostrar directamente."
    )

    # 13. Roadmap
    pdf.chapter_title("13", "Roadmap (proximas versiones)")
    pdf.kv_table([
        ("V-1.1.x", "Contexto taxonomy (ciclos, cursos, asignaturas configurables)"),
        ("V-1.2.x", "Frontend React - catalogo publico + panel de editor"),
        ("V-1.3.x", "Contexto media (imagenes y ficheros adjuntos)"),
        ("V-1.4.x", "Contexto auditing + analytics (visitas anonimas y agregadas)"),
        ("V-1.5.x", "Contexto configuration (nombre del sitio, logotipo)"),
        ("V-2.0.0", "Busqueda FTS5, E2E con Playwright, zona de adultos con anuncios"),
    ])

    pdf.output(output_path)
    print("PDF generado: " + output_path)


if __name__ == "__main__":
    import os
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual-v0.1.0.pdf")
    build_pdf(output)
