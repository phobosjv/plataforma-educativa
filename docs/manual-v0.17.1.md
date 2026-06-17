# Manual Técnico y de Usuario — Plataforma Educativa V-0.17.1

**Fecha:** 2026-06-17  
**Versión:** V-0.17.1  
**Estado:** Desarrollo activo

---

## 0. Novedades de V-0.17.1 (robustez / seguridad)

**Migración de JWT de `python-jose` a `PyJWT`.**

- La gestión de tokens JWT (HS256) pasa de `python-jose` a **`PyJWT`**. Motivo: `python-jose` arrastra
  un historial de CVEs y un mantenimiento irregular; `PyJWT` es la librería de referencia y mejor
  mantenida del ecosistema.
- El cambio está **aislado en `auth_service.py`** (codificar/decodificar HS256). **No cambia el
  comportamiento, ni la API, ni el esquema de datos**: los tokens emitidos siguen siendo HS256 y
  válidos; el login y las guardas de rol funcionan igual.
- Beneficio colateral: `PyJWT` **avisa si la `SECRET_KEY` es más corta de 32 bytes**, reforzando la
  recomendación (ya documentada) de usar una clave larga y aleatoria en producción.
- Dependencia: `python-jose[cryptography]` → `pyjwt`. 201 tests de backend en verde (5 nuevos del
  servicio de auth). API version → `0.17.1`.

> El resto de la aplicación (funcionalidad, endpoints, modelo de datos, despliegue) es **idéntico a
> V-0.17.0**; consulta `docs/manual-v0.17.0.(md|pdf)` para el manual completo.

---

## 1. Qué revisar al actualizar

- **`SECRET_KEY`**: asegúrate de que en producción es **larga (≥ 32 caracteres) y aleatoria**. Si es
  corta, en los logs aparecerá un aviso de `PyJWT` (`InsecureKeyLengthWarning`). No es un error, pero
  conviene corregirlo: cambia `SECRET_KEY` en el `.env` por una clave robusta.

  > Cambiar `SECRET_KEY` invalida los tokens ya emitidos: los usuarios tendrán que volver a iniciar
  > sesión (efecto inofensivo y puntual).

- **Dependencias**: la imagen del backend ya no instala `python-jose`; instala `pyjwt`. Al reconstruir
  con Docker (`docker compose up -d --build`) se aplica automáticamente.

---

## 2. Despliegue (sin cambios respecto a V-0.17.0)

```bash
# En el servidor, desde /opt
tar czf backup-$(date +%F-%H%M).tgz -C plataforma-educativa data media .env
unzip -oq plataforma-educativa-v0.17.1.zip
cp -rf plataforma-educativa-v0.17.1/. plataforma-educativa/
cd plataforma-educativa && docker compose up -d --build
```

No hay migraciones nuevas. El contenido (`data/`, `media/`) no se toca.

---

## 3. Tests

```bash
cd backend && python -m pytest tests/unit tests/integration -q   # 201 tests
```

Tests nuevos (`tests/unit/test_auth_service.py`): round-trip de token, token inválido, token con
secreto distinto, token expirado y hash/verify de contraseña (Argon2id).

---

## 4. Roadmap

- **Hecho (V-0.17.1):** migración `python-jose` → `PyJWT` (robustez).
- **Hecho (V-0.17.0):** historial de versiones y restauración de contenidos.
- **Pendiente de robustez:** ejecutar el backend como **usuario no-root** en Docker (`gosu` + `chown`
  en el entrypoint); requiere validación en el servidor (no se puede probar Docker en la máquina de
  desarrollo).
