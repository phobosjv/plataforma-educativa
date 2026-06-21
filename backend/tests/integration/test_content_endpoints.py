"""Tests de integración para los endpoints del contexto CONTENIDO."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.contexts.identity.domain.model import Rol, Usuario
from app.contexts.identity.infrastructure.auth_service import ArgonAuthService
from app.contexts.identity.infrastructure.repositories import SqlAlchemyUsuarioRepository
from app.main import app
from app.shared.infrastructure.database import Base, get_db

_TEST_DB_URL = "sqlite://"


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        _TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _create_user_and_token(db: Session, client: TestClient, email: str, rol: Rol) -> str:
    auth = ArgonAuthService("test-secret", 60)
    repo = SqlAlchemyUsuarioRepository(db)
    usuario = Usuario.crear(email, auth.hash_password("password1"), rol)
    repo.add(usuario)
    db.commit()
    r = client.post("/api/v1/auth/token", data={"username": email, "password": "password1"})
    assert r.status_code == 200
    return str(r.json()["access_token"])


@pytest.fixture()
def editor_token(db_session: Session, client: TestClient) -> str:
    return _create_user_and_token(db_session, client, "editor@test.es", Rol.EDITOR)


@pytest.fixture()
def admin_token(db_session: Session, client: TestClient) -> str:
    return _create_user_and_token(db_session, client, "admin@test.es", Rol.ADMIN)


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _crear_contenido(client: TestClient, token: str, titulo: str = "Test") -> dict:  # type: ignore[type-arg]
    r = client.post(
        "/api/v1/contenidos/",
        json={"titulo": titulo, "tipo": "texto", "body_html": "<p>hola</p>"},
        headers=_headers(token),
    )
    assert r.status_code == 201
    return r.json()  # type: ignore[no-any-return]


class TestContenidosPublicos:
    def test_listar_sin_auth_devuelve_200(self, client: TestClient) -> None:
        r = client.get("/api/v1/contenidos/")
        assert r.status_code == 200
        assert r.json() == []

    def test_no_muestra_no_publicados(self, client: TestClient, editor_token: str) -> None:
        _crear_contenido(client, editor_token)
        r = client.get("/api/v1/contenidos/")
        assert r.json() == []

    def test_muestra_publicados(self, client: TestClient, editor_token: str) -> None:
        data = _crear_contenido(client, editor_token, "Publicado")
        client.post(f"/api/v1/contenidos/{data['id']}/publicar", headers=_headers(editor_token))
        r = client.get("/api/v1/contenidos/")
        assert len(r.json()) == 1


class TestContenidoCRUD:
    def test_crear_sin_auth_devuelve_401(self, client: TestClient) -> None:
        r = client.post("/api/v1/contenidos/", json={"titulo": "X", "tipo": "texto"})
        assert r.status_code == 401

    def test_editor_puede_crear(self, client: TestClient, editor_token: str) -> None:
        data = _crear_contenido(client, editor_token)
        assert data["titulo"] == "Test"
        assert data["publicado"] is False

    def test_obtener_contenido_no_existe_devuelve_404(self, client: TestClient) -> None:
        r = client.get("/api/v1/contenidos/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404

    def test_soft_delete_y_no_aparece_en_lista(self, client: TestClient, editor_token: str) -> None:
        data = _crear_contenido(client, editor_token)
        uid = data["id"]
        # Publicar → listar → borrar → listar
        client.post(f"/api/v1/contenidos/{uid}/publicar", headers=_headers(editor_token))
        r = client.get("/api/v1/contenidos/")
        assert len(r.json()) == 1

        client.delete(f"/api/v1/contenidos/{uid}", headers=_headers(editor_token))
        r = client.get("/api/v1/contenidos/")
        assert r.json() == []

    def test_restaurar_contenido(self, client: TestClient, editor_token: str) -> None:
        data = _crear_contenido(client, editor_token)
        uid = data["id"]
        client.delete(f"/api/v1/contenidos/{uid}", headers=_headers(editor_token))
        r = client.post(f"/api/v1/contenidos/{uid}/restaurar", headers=_headers(editor_token))
        assert r.status_code == 200
        assert r.json()["borrado"] is False

    def test_publicar_contenido(self, client: TestClient, editor_token: str) -> None:
        data = _crear_contenido(client, editor_token)
        uid = data["id"]
        r = client.post(f"/api/v1/contenidos/{uid}/publicar", headers=_headers(editor_token))
        assert r.status_code == 200
        assert r.json()["publicado"] is True

    def test_no_publica_interactivo_sin_html(self, client: TestClient, editor_token: str) -> None:
        uid = client.post(
            "/api/v1/contenidos/",
            json={"titulo": "Ejercicio sin fichero", "tipo": "interactivo"},
            headers=_headers(editor_token),
        ).json()["id"]
        r = client.post(f"/api/v1/contenidos/{uid}/publicar", headers=_headers(editor_token))
        assert r.status_code == 400
        assert "fichero" in r.json()["detail"].lower()
        # No quedó publicado.
        assert client.get(f"/api/v1/contenidos/{uid}").json()["publicado"] is False

    def test_crear_interactivo_marcado_examen(self, client: TestClient, editor_token: str) -> None:
        r = client.post(
            "/api/v1/contenidos/",
            json={"titulo": "Simulacro", "tipo": "interactivo", "es_examen": True},
            headers=_headers(editor_token),
        )
        assert r.status_code == 201
        assert r.json()["es_examen"] is True

    def test_no_marca_texto_como_examen(self, client: TestClient, editor_token: str) -> None:
        r = client.post(
            "/api/v1/contenidos/",
            json={"titulo": "Art", "tipo": "texto", "body_html": "<p>x</p>", "es_examen": True},
            headers=_headers(editor_token),
        )
        assert r.status_code == 400
        assert "examen" in r.json()["detail"].lower()

    def test_actualizar_marca_examen(self, client: TestClient, editor_token: str) -> None:
        uid = client.post(
            "/api/v1/contenidos/",
            json={"titulo": "Ej", "tipo": "interactivo"},
            headers=_headers(editor_token),
        ).json()["id"]
        r = client.put(
            f"/api/v1/contenidos/{uid}",
            json={"es_examen": True},
            headers=_headers(editor_token),
        )
        assert r.status_code == 200
        assert r.json()["es_examen"] is True
        # Desmarcar también funciona.
        r2 = client.put(
            f"/api/v1/contenidos/{uid}",
            json={"es_examen": False},
            headers=_headers(editor_token),
        )
        assert r2.json()["es_examen"] is False


class TestAdminEndpoints:
    def test_admin_ve_papelera(
        self, client: TestClient, editor_token: str, admin_token: str
    ) -> None:
        data = _crear_contenido(client, editor_token)
        uid = data["id"]
        client.delete(f"/api/v1/contenidos/{uid}", headers=_headers(editor_token))

        r = client.get("/api/v1/admin/contenidos/", headers=_headers(admin_token))
        assert r.status_code == 200
        ids = [c["id"] for c in r.json()]
        assert uid in ids

    def test_editor_no_puede_acceder_admin(self, client: TestClient, editor_token: str) -> None:
        r = client.get("/api/v1/admin/contenidos/", headers=_headers(editor_token))
        assert r.status_code == 403


class TestPurgaDefinitiva:
    """Eliminación definitiva de contenido desde la papelera (solo admin, irreversible)."""

    def test_purgar_desde_papelera_elimina(
        self, client: TestClient, editor_token: str, admin_token: str
    ) -> None:
        uid = _crear_contenido(client, editor_token)["id"]
        client.delete(f"/api/v1/contenidos/{uid}", headers=_headers(editor_token))  # a papelera
        r = client.delete(f"/api/v1/contenidos/{uid}/purgar", headers=_headers(admin_token))
        assert r.status_code == 204
        # Ya no aparece ni en la vista admin (que incluye papelera).
        admin = client.get("/api/v1/admin/contenidos/", headers=_headers(admin_token))
        assert uid not in [c["id"] for c in admin.json()]

    def test_purgar_no_borrado_devuelve_400(
        self, client: TestClient, editor_token: str, admin_token: str
    ) -> None:
        uid = _crear_contenido(client, editor_token)["id"]  # NO está en la papelera
        r = client.delete(f"/api/v1/contenidos/{uid}/purgar", headers=_headers(admin_token))
        assert r.status_code == 400

    def test_purgar_requiere_admin(self, client: TestClient, editor_token: str) -> None:
        uid = _crear_contenido(client, editor_token)["id"]
        client.delete(f"/api/v1/contenidos/{uid}", headers=_headers(editor_token))
        r = client.delete(f"/api/v1/contenidos/{uid}/purgar", headers=_headers(editor_token))
        assert r.status_code == 403


class TestTaxonomiaDeContenido:
    """La clasificación se expone en el contrato y puede asignarse/editarse (V-0.6.1)."""

    _CICLO = "11111111-1111-1111-1111-111111111111"
    _CURSO = "22222222-2222-2222-2222-222222222222"
    _ASIG = "33333333-3333-3333-3333-333333333333"

    def test_crear_con_taxonomia_se_devuelve(self, client: TestClient, editor_token: str) -> None:
        r = client.post(
            "/api/v1/contenidos/",
            json={
                "titulo": "Con taxonomia",
                "tipo": "texto",
                "ciclo_id": self._CICLO,
                "curso_id": self._CURSO,
                "asignatura_id": self._ASIG,
            },
            headers=_headers(editor_token),
        )
        assert r.status_code == 201
        body = r.json()
        assert body["ciclo_id"] == self._CICLO
        assert body["curso_id"] == self._CURSO
        assert body["asignatura_id"] == self._ASIG

    def test_editar_reasigna_taxonomia(self, client: TestClient, editor_token: str) -> None:
        uid = _crear_contenido(client, editor_token)["id"]  # sin taxonomia
        r = client.put(
            f"/api/v1/contenidos/{uid}",
            json={"ciclo_id": self._CICLO, "curso_id": self._CURSO, "asignatura_id": self._ASIG},
            headers=_headers(editor_token),
        )
        assert r.status_code == 200
        assert r.json()["ciclo_id"] == self._CICLO
        # Verificar PERSISTENCIA con un GET posterior (no solo la respuesta del PUT).
        g = client.get(f"/api/v1/contenidos/{uid}")
        assert g.json()["ciclo_id"] == self._CICLO
        assert g.json()["curso_id"] == self._CURSO
        assert g.json()["asignatura_id"] == self._ASIG

    def test_editar_sin_taxonomia_no_la_borra(self, client: TestClient, editor_token: str) -> None:
        # Crear con taxonomia, luego PUT que NO incluye campos de taxonomia.
        uid = client.post(
            "/api/v1/contenidos/",
            json={"titulo": "X", "tipo": "texto", "ciclo_id": self._CICLO},
            headers=_headers(editor_token),
        ).json()["id"]
        r = client.put(
            f"/api/v1/contenidos/{uid}",
            json={"titulo": "X2"},
            headers=_headers(editor_token),
        )
        assert r.status_code == 200
        assert r.json()["ciclo_id"] == self._CICLO  # se conserva

    def test_editar_desasigna_taxonomia_con_null(
        self, client: TestClient, editor_token: str
    ) -> None:
        uid = client.post(
            "/api/v1/contenidos/",
            json={"titulo": "X", "tipo": "texto", "ciclo_id": self._CICLO},
            headers=_headers(editor_token),
        ).json()["id"]
        r = client.put(
            f"/api/v1/contenidos/{uid}",
            json={"ciclo_id": None},
            headers=_headers(editor_token),
        )
        assert r.status_code == 200
        assert r.json()["ciclo_id"] is None  # desasignado explícitamente


class TestSubirHtmlInteractivo:
    """Subida del fichero HTML de un ejercicio interactivo (CLAUDE.md §10)."""

    _HTML = b"<html><body><script>document.body.textContent='hola'</script></body></html>"

    def _crear_interactivo(self, client: TestClient, token: str) -> str:
        r = client.post(
            "/api/v1/contenidos/",
            json={"titulo": "Juego", "tipo": "interactivo"},
            headers=_headers(token),
        )
        assert r.status_code == 201
        return str(r.json()["id"])

    def test_subir_html_fija_hash_y_sandbox_url(
        self, client: TestClient, editor_token: str, tmp_path, monkeypatch  # type: ignore[no-untyped-def]
    ) -> None:
        from app.config import settings

        monkeypatch.setattr(settings, "media_dir", str(tmp_path))
        uid = self._crear_interactivo(client, editor_token)
        r = client.post(
            f"/api/v1/contenidos/{uid}/html",
            files={"fichero": ("ej.html", self._HTML, "text/html")},
            headers=_headers(editor_token),
        )
        assert r.status_code == 200
        body = r.json()
        assert body["hash_html"] is not None
        assert body["sandbox_url"].endswith(f"/ejercicio/{body['hash_html']}")
        # El fichero se escribió content-addressed (sin sanear).
        h = body["hash_html"]
        assert (tmp_path / h[:2] / f"{h}.html").read_bytes() == self._HTML

    def test_subir_html_a_tipo_texto_devuelve_400(
        self, client: TestClient, editor_token: str, tmp_path, monkeypatch  # type: ignore[no-untyped-def]
    ) -> None:
        from app.config import settings

        monkeypatch.setattr(settings, "media_dir", str(tmp_path))
        uid = _crear_contenido(client, editor_token)["id"]  # tipo texto
        r = client.post(
            f"/api/v1/contenidos/{uid}/html",
            files={"fichero": ("ej.html", self._HTML, "text/html")},
            headers=_headers(editor_token),
        )
        assert r.status_code == 400

    def test_subir_html_sin_auth_devuelve_401(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/contenidos/00000000-0000-0000-0000-000000000000/html",
            files={"fichero": ("ej.html", self._HTML, "text/html")},
        )
        assert r.status_code == 401

    def test_subir_html_vacio_devuelve_400(
        self, client: TestClient, editor_token: str, tmp_path, monkeypatch  # type: ignore[no-untyped-def]
    ) -> None:
        from app.config import settings

        monkeypatch.setattr(settings, "media_dir", str(tmp_path))
        uid = self._crear_interactivo(client, editor_token)
        r = client.post(
            f"/api/v1/contenidos/{uid}/html",
            files={"fichero": ("ej.html", b"", "text/html")},
            headers=_headers(editor_token),
        )
        assert r.status_code == 400


class TestSubirPdfFicha:
    """Subida del fichero PDF de una ficha imprimible (tercer tipo de contenido)."""

    _PDF = b"%PDF-1.7\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"

    def _crear_pdf(self, client: TestClient, token: str, titulo: str = "Ficha de letras") -> str:
        r = client.post(
            "/api/v1/contenidos/",
            json={"titulo": titulo, "tipo": "pdf"},
            headers=_headers(token),
        )
        assert r.status_code == 201
        return str(r.json()["id"])

    def test_subir_pdf_fija_hash_y_urls(
        self, client: TestClient, editor_token: str, tmp_path, monkeypatch  # type: ignore[no-untyped-def]
    ) -> None:
        from app.config import settings

        monkeypatch.setattr(settings, "media_dir", str(tmp_path))
        uid = self._crear_pdf(client, editor_token)
        r = client.post(
            f"/api/v1/contenidos/{uid}/pdf",
            files={"fichero": ("ficha.pdf", self._PDF, "application/pdf")},
            headers=_headers(editor_token),
        )
        assert r.status_code == 200
        body = r.json()
        h = body["hash_pdf"]
        assert h is not None
        assert body["pdf_url"].endswith(f"/ficha/{h}.pdf")
        assert "descargar=1" in body["pdf_descarga_url"]
        # El fichero se escribió content-addressed (sin modificar).
        assert (tmp_path / h[:2] / f"{h}.pdf").read_bytes() == self._PDF

    def test_pdf_se_puede_publicar_con_fichero(
        self, client: TestClient, editor_token: str, tmp_path, monkeypatch  # type: ignore[no-untyped-def]
    ) -> None:
        from app.config import settings

        monkeypatch.setattr(settings, "media_dir", str(tmp_path))
        uid = self._crear_pdf(client, editor_token)
        # Sin fichero, no se puede publicar.
        r = client.post(f"/api/v1/contenidos/{uid}/publicar", headers=_headers(editor_token))
        assert r.status_code == 400
        # Con fichero, sí.
        client.post(
            f"/api/v1/contenidos/{uid}/pdf",
            files={"fichero": ("ficha.pdf", self._PDF, "application/pdf")},
            headers=_headers(editor_token),
        )
        r = client.post(f"/api/v1/contenidos/{uid}/publicar", headers=_headers(editor_token))
        assert r.status_code == 200
        assert r.json()["publicado"] is True

    def test_subir_pdf_a_tipo_texto_devuelve_400(
        self, client: TestClient, editor_token: str, tmp_path, monkeypatch  # type: ignore[no-untyped-def]
    ) -> None:
        from app.config import settings

        monkeypatch.setattr(settings, "media_dir", str(tmp_path))
        uid = _crear_contenido(client, editor_token)["id"]  # tipo texto
        r = client.post(
            f"/api/v1/contenidos/{uid}/pdf",
            files={"fichero": ("ficha.pdf", self._PDF, "application/pdf")},
            headers=_headers(editor_token),
        )
        assert r.status_code == 400

    def test_subir_fichero_no_pdf_devuelve_400(
        self, client: TestClient, editor_token: str, tmp_path, monkeypatch  # type: ignore[no-untyped-def]
    ) -> None:
        from app.config import settings

        monkeypatch.setattr(settings, "media_dir", str(tmp_path))
        uid = self._crear_pdf(client, editor_token)
        r = client.post(
            f"/api/v1/contenidos/{uid}/pdf",
            files={"fichero": ("falso.pdf", b"esto no es un pdf", "application/pdf")},
            headers=_headers(editor_token),
        )
        assert r.status_code == 400

    def test_subir_pdf_sin_auth_devuelve_401(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/contenidos/00000000-0000-0000-0000-000000000000/pdf",
            files={"fichero": ("ficha.pdf", self._PDF, "application/pdf")},
        )
        assert r.status_code == 401


class TestVersionado:
    """Historial de versiones y restauración (CLAUDE.md §7: restaurar nunca destruye)."""

    def _crear_y_editar(self, client: TestClient, token: str) -> str:
        uid = client.post(
            "/api/v1/contenidos/",
            json={"titulo": "Titulo A", "tipo": "texto", "body_html": "<p>A</p>"},
            headers=_headers(token),
        ).json()["id"]
        client.put(
            f"/api/v1/contenidos/{uid}",
            json={"titulo": "Titulo B", "body_html": "<p>B</p>"},
            headers=_headers(token),
        )
        return str(uid)

    def test_listar_versiones(self, client: TestClient, editor_token: str) -> None:
        uid = self._crear_y_editar(client, editor_token)
        r = client.get(f"/api/v1/contenidos/{uid}/versiones", headers=_headers(editor_token))
        assert r.status_code == 200
        versiones = r.json()
        assert [v["version_no"] for v in versiones] == [1, 2]
        assert versiones[0]["titulo"] == "Titulo A"
        assert versiones[1]["titulo"] == "Titulo B"
        # El autor de cada versión se resuelve a su email (CLAUDE.md: vía caso de uso de identity).
        assert all(v["created_by_email"] == "editor@test.es" for v in versiones)

    def test_restaurar_version_revierte_y_crea_nueva(
        self, client: TestClient, editor_token: str
    ) -> None:
        uid = self._crear_y_editar(client, editor_token)  # v1=A, v2=B (actual)
        r = client.post(
            f"/api/v1/contenidos/{uid}/versiones/1/restaurar", headers=_headers(editor_token)
        )
        assert r.status_code == 200
        assert r.json()["titulo"] == "Titulo A"
        assert r.json()["body_html"] == "<p>A</p>"
        # Restaurar NO destruye: se creó una v3, el historial sigue creciendo.
        versiones = client.get(
            f"/api/v1/contenidos/{uid}/versiones", headers=_headers(editor_token)
        ).json()
        assert [v["version_no"] for v in versiones] == [1, 2, 3]
        assert versiones[2]["titulo"] == "Titulo A"
        # La lectura pública del contenido refleja el estado restaurado.
        client.post(f"/api/v1/contenidos/{uid}/publicar", headers=_headers(editor_token))
        assert client.get(f"/api/v1/contenidos/{uid}").json()["titulo"] == "Titulo A"

    def test_restaurar_version_inexistente_devuelve_404(
        self, client: TestClient, editor_token: str
    ) -> None:
        uid = self._crear_y_editar(client, editor_token)
        r = client.post(
            f"/api/v1/contenidos/{uid}/versiones/99/restaurar", headers=_headers(editor_token)
        )
        assert r.status_code == 404

    def test_versiones_requiere_editor(self, client: TestClient) -> None:
        r = client.get("/api/v1/contenidos/00000000-0000-0000-0000-000000000000/versiones")
        assert r.status_code == 401


class TestSanitizacionArticulos:
    """El HTML de artículos (tipo=texto) se sanea SIEMPRE en servidor (CLAUDE.md §10)."""

    _MALICIOSO = (
        '<p>Hola</p><script>alert(1)</script>'
        '<img src=x onerror="alert(2)">'
        '<a href="javascript:alert(3)">clic</a>'
    )

    def test_crear_texto_elimina_script_y_eventos(
        self, client: TestClient, editor_token: str
    ) -> None:
        r = client.post(
            "/api/v1/contenidos/",
            json={"titulo": "Articulo", "tipo": "texto", "body_html": self._MALICIOSO},
            headers=_headers(editor_token),
        )
        assert r.status_code == 201
        body = r.json()["body_html"]
        assert "<script>" not in body
        assert "onerror" not in body
        assert "javascript:" not in body
        assert "<p>Hola</p>" in body  # el contenido seguro se conserva

    def test_actualizar_texto_sanitiza(
        self, client: TestClient, editor_token: str
    ) -> None:
        uid = _crear_contenido(client, editor_token)["id"]
        r = client.put(
            f"/api/v1/contenidos/{uid}",
            json={"body_html": self._MALICIOSO},
            headers=_headers(editor_token),
        )
        assert r.status_code == 200
        body = r.json()["body_html"]
        assert "<script>" not in body and "onerror" not in body
