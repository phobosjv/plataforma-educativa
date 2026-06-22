"""Modelo de dominio del contexto CONFIGURATION. SIN dependencias de framework."""

from __future__ import annotations

import json
from dataclasses import dataclass
from uuid import UUID

from app.shared.domain.base import DomainError, Entity

SINGLETON_ID = UUID("00000000-0000-0000-0000-000000000001")

# Catálogo de fuentes seleccionables. El identificador "sistema" usa la pila de
# fuentes nativa del dispositivo (sin descarga); el resto son fuentes self-hosted
# servidas por la propia app (no desde un CDN externo) para no exponer la IP de
# los menores a terceros (CLAUDE.md §10). El dominio solo conoce los IDs válidos;
# los ficheros y la familia CSS concreta viven en el frontend.
FUENTES_PERMITIDAS: frozenset[str] = frozenset(
    {"sistema", "nunito", "quicksand", "lexend", "atkinson", "andika"}
)

# Catálogo de fondos/estampados temáticos. "ninguno" deja el fondo liso. El resto
# son patrones SVG self-hosted (servidos por la app) que se recolorean con la paleta
# activa a baja opacidad. El dominio solo conoce los IDs válidos.
FONDOS_PERMITIDOS: frozenset[str] = frozenset(
    {"ninguno", "classroom", "naturaleza", "espacio", "oceano", "geometrico", "granja"}
)

# Disposición del estampado: "ordenado" repite el tile fijo; "desordenado" genera un
# patrón disperso (posición/rotación/escala variables) en el que dos iconos iguales nunca
# quedan adyacentes. El dominio solo conoce los IDs válidos; la generación vive en el frontend.
ESTILOS_FONDO_PERMITIDOS: frozenset[str] = frozenset({"ordenado", "desordenado"})

LONGITUD_MAX_NOMBRE = 80
LONGITUD_MAX_AULA_ABIERTA = 40
LONGITUD_MAX_EMOJI = 8
LONGITUD_MAX_LOGO_URL = 500

# El logo es una imagen subida por el contexto MEDIA, que la sirve direccionada por
# contenido bajo /media/images/. El dominio solo acepta referencias a ese origen propio
# (o cadena vacía = sin logo): así nunca guardamos una URL externa que pudiera filtrar la
# IP de los menores a terceros (CLAUDE.md §10) ni inyectar un origen arbitrario en la cabecera.
PREFIJO_LOGO_PERMITIDO = "/media/"

LONGITUD_MAX_CATALOGO_TEXTO = 120
# Tope del fragmento HTML de un anuncio (código de la red de anuncios pegado por el admin).
LONGITUD_MAX_PUBLICIDAD = 8000
MAX_ENLACES_DONACION = 12
LONGITUD_MAX_DONACION_ETIQUETA = 40
LONGITUD_MAX_URL = 500
# Las URLs de donación las pega el admin y se renderizan como enlaces en la zona pública.
# Solo se admiten esquemas web para no abrir un vector de inyección (javascript:, data:, …).
ESQUEMAS_URL_PERMITIDOS = ("https://", "http://")


@dataclass
class EnlaceDonacion:
    """Enlace a una plataforma de donación (p. ej. PayPal, Ko-fi). Mostrado en la zona pública."""

    etiqueta: str
    url: str

    def to_dict(self) -> dict[str, str]:
        return {"etiqueta": self.etiqueta, "url": self.url}


# Redes sociales soportadas en el pie público. El dominio solo conoce los IDs válidos; el
# icono (SVG self-hosted, sin CDN externo por la privacidad de los menores, §10) vive en el frontend.
REDES_SOCIALES_PERMITIDAS: frozenset[str] = frozenset(
    {"facebook", "instagram", "x", "youtube", "tiktok", "whatsapp", "telegram", "linkedin"}
)
MAX_REDES_SOCIALES = 10


@dataclass
class EnlaceRedSocial:
    """Enlace a un perfil del sitio en una red social (mostrado con su icono en el pie)."""

    red: str
    url: str

    def to_dict(self) -> dict[str, str]:
        return {"red": self.red, "url": self.url}


@dataclass
class PaletaPersonalizada:
    id: str
    nombre: str
    bg: str
    surface: str
    fg: str
    primary: str

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "bg": self.bg,
            "surface": self.surface,
            "fg": self.fg,
            "primary": self.primary,
        }


@dataclass
class ConfiguracionSitio(Entity):
    nombre_sitio: str = "Plataforma Educativa"
    paleta_activa: str = "cielo"
    paletas_json: str = "[]"
    fuente_activa: str = "sistema"
    fondo_activo: str = "ninguno"
    fondo_estilo: str = "ordenado"
    # Logo del sitio: URL relativa a una imagen del propio origen (/media/images/...) o
    # cadena vacía si no hay logo (entonces el frontend muestra solo el nombre).
    logo_url: str = ""
    # Etiqueta y emoji de la entrada a las asignaturas transversales en el catálogo. El
    # nombre lo decide cada centro (p. ej. "Aula Abierta", "Diversidad") para evitar
    # términos que puedan estigmatizar al alumnado con esas necesidades.
    aula_abierta_label: str = "Aula Abierta"
    aula_abierta_emoji: str = "🌟"
    # Textos de la pantalla inicial del catálogo. Configurables porque, si hay publicidad,
    # se redactan dirigidos a los padres (no al alumnado).
    catalogo_titulo: str = "¿En qué curso estás?"
    catalogo_subtitulo: str = "Toca tu curso para ver las actividades"
    # Enlaces de donación (PayPal y otras plataformas) mostrados en la zona pública.
    donaciones_json: str = "[]"
    # Enlaces a redes sociales del sitio, mostrados con su icono en el pie público.
    redes_sociales_json: str = "[]"
    # Publicidad en los márgenes de las pantallas públicas de navegación (zona de adultos,
    # §10). Nunca se muestra durante un ejercicio (lo usa un menor) ni en el panel.
    publicidad_activa: bool = False
    publicidad_html_izquierda: str = ""
    publicidad_html_derecha: str = ""
    # Controla si el badge de versión (cms-version) se muestra junto al nombre del sitio.
    mostrar_version: bool = True

    @classmethod
    def singleton(cls) -> "ConfiguracionSitio":
        return cls(id=SINGLETON_ID)

    @property
    def paletas_personalizadas(self) -> list[PaletaPersonalizada]:
        return [PaletaPersonalizada(**p) for p in json.loads(self.paletas_json)]

    @property
    def donaciones(self) -> list[EnlaceDonacion]:
        return [EnlaceDonacion(**d) for d in json.loads(self.donaciones_json)]

    @property
    def redes_sociales(self) -> list[EnlaceRedSocial]:
        return [EnlaceRedSocial(**d) for d in json.loads(self.redes_sociales_json)]

    def cambiar_nombre(self, nombre: str) -> None:
        nombre = nombre.strip()
        if not nombre:
            raise DomainError("El nombre del sitio no puede estar vacío.")
        if len(nombre) > LONGITUD_MAX_NOMBRE:
            raise DomainError(
                f"El nombre del sitio no puede superar {LONGITUD_MAX_NOMBRE} caracteres."
            )
        self.nombre_sitio = nombre

    def cambiar_fuente(self, fuente_id: str) -> None:
        if fuente_id not in FUENTES_PERMITIDAS:
            raise DomainError(f"Fuente '{fuente_id}' no permitida.")
        self.fuente_activa = fuente_id

    def cambiar_fondo(self, fondo_id: str) -> None:
        if fondo_id not in FONDOS_PERMITIDOS:
            raise DomainError(f"Fondo '{fondo_id}' no permitido.")
        self.fondo_activo = fondo_id

    def cambiar_estilo_fondo(self, estilo: str) -> None:
        if estilo not in ESTILOS_FONDO_PERMITIDOS:
            raise DomainError(f"Estilo de fondo '{estilo}' no permitido.")
        self.fondo_estilo = estilo

    def cambiar_logo(self, logo_url: str) -> None:
        logo_url = logo_url.strip()
        if not logo_url:
            self.logo_url = ""
            return
        if len(logo_url) > LONGITUD_MAX_LOGO_URL:
            raise DomainError("La URL del logo es demasiado larga.")
        if not logo_url.startswith(PREFIJO_LOGO_PERMITIDO):
            raise DomainError("El logo debe ser una imagen subida al propio sitio.")
        self.logo_url = logo_url

    def cambiar_textos_catalogo(self, titulo: str, subtitulo: str) -> None:
        titulo = titulo.strip()
        subtitulo = subtitulo.strip()
        if not titulo:
            raise DomainError("El título del catálogo no puede estar vacío.")
        if len(titulo) > LONGITUD_MAX_CATALOGO_TEXTO or len(subtitulo) > LONGITUD_MAX_CATALOGO_TEXTO:
            raise DomainError(
                f"Los textos del catálogo no pueden superar {LONGITUD_MAX_CATALOGO_TEXTO} caracteres."
            )
        self.catalogo_titulo = titulo
        self.catalogo_subtitulo = subtitulo

    def cambiar_donaciones(self, enlaces: list[EnlaceDonacion]) -> None:
        if len(enlaces) > MAX_ENLACES_DONACION:
            raise DomainError(f"No se permiten más de {MAX_ENLACES_DONACION} enlaces de donación.")
        normalizados: list[EnlaceDonacion] = []
        for e in enlaces:
            etiqueta = e.etiqueta.strip()
            url = e.url.strip()
            if not etiqueta or not url:
                raise DomainError("Cada enlace de donación necesita una etiqueta y una URL.")
            if len(etiqueta) > LONGITUD_MAX_DONACION_ETIQUETA:
                raise DomainError(
                    f"La etiqueta de donación no puede superar {LONGITUD_MAX_DONACION_ETIQUETA} caracteres."
                )
            if len(url) > LONGITUD_MAX_URL or not url.startswith(ESQUEMAS_URL_PERMITIDOS):
                raise DomainError("La URL de donación debe empezar por http:// o https://.")
            normalizados.append(EnlaceDonacion(etiqueta=etiqueta, url=url))
        self.donaciones_json = json.dumps(
            [e.to_dict() for e in normalizados], ensure_ascii=False
        )

    def cambiar_redes_sociales(self, enlaces: list[EnlaceRedSocial]) -> None:
        if len(enlaces) > MAX_REDES_SOCIALES:
            raise DomainError(f"No se permiten más de {MAX_REDES_SOCIALES} redes sociales.")
        normalizados: list[EnlaceRedSocial] = []
        vistas: set[str] = set()
        for e in enlaces:
            red = e.red.strip().lower()
            url = e.url.strip()
            if red not in REDES_SOCIALES_PERMITIDAS:
                raise DomainError(f"Red social '{e.red}' no soportada.")
            if red in vistas:
                raise DomainError(f"Red social '{red}' duplicada.")
            if not url or len(url) > LONGITUD_MAX_URL or not url.startswith(ESQUEMAS_URL_PERMITIDOS):
                raise DomainError("La URL de la red social debe empezar por http:// o https://.")
            vistas.add(red)
            normalizados.append(EnlaceRedSocial(red=red, url=url))
        self.redes_sociales_json = json.dumps(
            [e.to_dict() for e in normalizados], ensure_ascii=False
        )

    def cambiar_publicidad(self, activa: bool, html_izquierda: str, html_derecha: str) -> None:
        if (
            len(html_izquierda) > LONGITUD_MAX_PUBLICIDAD
            or len(html_derecha) > LONGITUD_MAX_PUBLICIDAD
        ):
            raise DomainError(
                f"El código de publicidad no puede superar {LONGITUD_MAX_PUBLICIDAD} caracteres."
            )
        self.publicidad_activa = activa
        self.publicidad_html_izquierda = html_izquierda
        self.publicidad_html_derecha = html_derecha

    def cambiar_aula_abierta(self, label: str, emoji: str) -> None:
        label = label.strip()
        if not label:
            raise DomainError("La etiqueta de Aula Abierta no puede estar vacía.")
        if len(label) > LONGITUD_MAX_AULA_ABIERTA:
            raise DomainError(
                f"La etiqueta de Aula Abierta no puede superar {LONGITUD_MAX_AULA_ABIERTA} caracteres."
            )
        emoji = emoji.strip()
        if len(emoji) > LONGITUD_MAX_EMOJI:
            raise DomainError("El emoji de Aula Abierta es demasiado largo.")
        self.aula_abierta_label = label
        self.aula_abierta_emoji = emoji

    def activar_paleta(self, paleta_id: str) -> None:
        self.paleta_activa = paleta_id

    def agregar_paleta(self, paleta: PaletaPersonalizada) -> None:
        paletas = self.paletas_personalizadas
        if any(p.id == paleta.id for p in paletas):
            raise DomainError(f"Ya existe una paleta con id '{paleta.id}'.")
        paletas.append(paleta)
        self.paletas_json = json.dumps([p.to_dict() for p in paletas])

    def actualizar_paleta(self, paleta: PaletaPersonalizada) -> None:
        paletas = [paleta if p.id == paleta.id else p for p in self.paletas_personalizadas]
        if not any(p.id == paleta.id for p in paletas):
            raise DomainError(f"Paleta '{paleta.id}' no encontrada.")
        self.paletas_json = json.dumps([p.to_dict() for p in paletas])

    def eliminar_paleta(self, paleta_id: str) -> None:
        if self.paleta_activa == paleta_id:
            raise DomainError("No se puede eliminar la paleta activa.")
        paletas = [p for p in self.paletas_personalizadas if p.id != paleta_id]
        self.paletas_json = json.dumps([p.to_dict() for p in paletas])
