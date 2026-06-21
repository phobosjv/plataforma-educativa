import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// El backend de desarrollo. Configurable por si corre en otro puerto.
const API_TARGET = process.env.VITE_API_TARGET ?? "http://localhost:8001";

// Hosts permitidos (Vite bloquea dominios desconocidos por seguridad; las IPs se permiten solas).
// VITE_ALLOWED_HOSTS: lista separada por comas (p. ej. "midominio.ddns.net,192.168.1.50").
// Usa "true" para permitir cualquier host (cómodo en pruebas, menos seguro).
const allowedHostsEnv = process.env.VITE_ALLOWED_HOSTS?.trim();
const allowedHosts =
  allowedHostsEnv === "true"
    ? true
    : allowedHostsEnv
      ? allowedHostsEnv.split(",").map((h) => h.trim()).filter(Boolean)
      : undefined; // sin configurar: comportamiento por defecto de Vite (localhost + IPs)

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // strictPort: si 5173 está ocupado, fallar en vez de saltar a 5174.
    // Evita que el frontend acabe en un puerto que el navegador/CORS no espera.
    strictPort: true,
    host: true,
    allowedHosts,
    // Proxy de /api al backend: el navegador habla siempre con el mismo
    // origen (localhost:5173), así que NO hay CORS en desarrollo.
    proxy: {
      "/api": {
        target: API_TARGET,
        changeOrigin: true,
      },
      // Imágenes de artículos servidas por el backend (origen de la app).
      "/media": {
        target: API_TARGET,
        changeOrigin: true,
      },
      // Fichas PDF: en dev el backend las sirve directamente (sin sandbox separado).
      // En prod, pdf_base_url apunta al subdominio sandbox; este proxy no interviene.
      "/ficha": {
        target: API_TARGET,
        changeOrigin: true,
      },
    },
  },
});
