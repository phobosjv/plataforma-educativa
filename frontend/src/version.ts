// Versión de la app, HORNEADA en el bundle del frontend en build-time. Se muestra junto al
// nombre del sitio (PublicLayout/AdminLayout) para verificar de un vistazo qué build está
// desplegado: si tras un despliegue NO ves el número nuevo, la imagen del frontend no se
// reconstruyó (usa `docker compose up -d --build`) y los assets (p. ej. el worker de PDF.js)
// siguen siendo los viejos.
//
// IMPORTANTE (CLAUDE.md §19): mantener sincronizada con `backend/app/version.py` en cada release.
export const APP_VERSION = "0.23.2";
