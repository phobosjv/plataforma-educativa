# Copias de seguridad, exportación y restauración

> Cómo se protege el contenido del sitio y cómo recuperarlo o migrarlo a otro servidor.

## 1. Qué se guarda y dónde

| Dato | Ubicación (host) | Tipo |
|---|---|---|
| Base de datos (contenidos, usuarios, configuración, taxonomía) | `./data/app.sqlite3` | bind mount |
| Ejercicios HTML + imágenes subidas | `./media/` | bind mount |
| Copias automáticas de la BD | `./data/backups/app-*.sqlite3` | bind mount |
| Espejo incremental de media | `./data/backups/media/` | bind mount |
| Certificados HTTPS | volumen `caddy_data` | volumen Docker |

Todo el **estado** vive en el host (`./data`, `./media`) y en el volumen `caddy_data`. Los
contenedores son desechables.

## 2. Copias automáticas (en segundo plano)

Cada ciclo (`BACKUP_INTERVAL_HOURS`, por defecto 24 h) la aplicación:

1. Hace una **copia en caliente** de la BD (online backup API, segura con WAL) en
   `./data/backups/` y conserva las `BACKUP_KEEP` más recientes (rotación).
2. Sincroniza un **espejo incremental** de `media` en `./data/backups/media/` (solo ficheros
   nuevos; son inmutables por hash). Desactivable con `MEDIA_BACKUP_ENABLED=false`.

> Estas copias viven en el **mismo disco** que los datos: protegen frente a borrados accidentales,
> pero NO frente a la pérdida del servidor. Para eso, usa la exportación completa y guárdala fuera.

## 3. Exportación completa (descarga off-site / migración)

Desde el panel admin → **Copias de seguridad** → **«Exportar todo (BD + media)»**, o por API:

```
POST /api/v1/admin/export        (solo admin)  → plataforma-export-YYYYMMDD-HHMMSS.tar.gz
```

El archivo contiene:

```
data/app.sqlite3     # copia consistente de la BD
media/...            # árbol completo de media
manifest.json        # formato, fecha, versión y nº de ficheros
```

**No incluye el `.env`** (secretos): ese se gestiona aparte en el servidor de destino.
Guarda el archivo en un lugar seguro (contiene los hashes Argon2id de las contraseñas).

## 4. Restaurar o migrar a otro servidor

No hay endpoint de importación (subir y sobrescribir la BD viva en caliente es arriesgado):
la restauración se hace en el servidor, con el stack parado.

```bash
cd /opt/plataforma-educativa

# 1. Parar el stack (sin -v: conserva certificados)
docker compose down

# 2. (Opcional, recomendado) respaldar lo que haya ahora
tar czf backup-previo-$(date +%F-%H%M).tgz data media .env 2>/dev/null || true

# 3. Limpiar data/media y restaurar desde el export
rm -rf data media
mkdir -p data media
tar xzf plataforma-export-YYYYMMDD-HHMMSS.tar.gz   # crea ./data/app.sqlite3 y ./media/...

# 4. Asegurar el .env (en migración: copiar/crear el del servidor nuevo)
#    Debe tener APP_DOMAIN, SANDBOX_DOMAIN, ACME_EMAIL, SECRET_KEY, admin…
#    IMPORTANTE: usa el MISMO SECRET_KEY que el origen si quieres que las sesiones
#    existentes sigan siendo válidas (si no, simplemente habrá que volver a iniciar sesión).

# 5. Permisos de media (nginx del sandbox lee como user nginx)
chmod -R a+rX media

# 6. Levantar
docker compose up -d --build
```

El entrypoint corre `alembic upgrade head` sobre la BD restaurada (la migra si hace falta) y,
como ya hay usuarios, **no** recrea el admin por defecto.

### Migración a un dominio distinto

Si cambias de dominio, ajusta `APP_DOMAIN`/`SANDBOX_DOMAIN` en el `.env` y los registros DNS;
Caddy emitirá certificados nuevos para los dominios nuevos en el primer arranque.

## 5. Verificación tras restaurar

```bash
docker compose ps                 # servicios "running"/"healthy"
docker compose logs --tail=30 api # alembic OK, sin recrear admin
```

En el navegador: entra en `https://APP_DOMAIN`, comprueba el catálogo y abre un ejercicio
interactivo (verifica que el sandbox sirve el HTML restaurado).
