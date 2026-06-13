import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// El backend de desarrollo. Configurable por si corre en otro puerto.
const API_TARGET = process.env.VITE_API_TARGET ?? "http://localhost:8001";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // strictPort: si 5173 está ocupado, fallar en vez de saltar a 5174.
    // Evita que el frontend acabe en un puerto que el navegador/CORS no espera.
    strictPort: true,
    host: true,
    // Proxy de /api al backend: el navegador habla siempre con el mismo
    // origen (localhost:5173), así que NO hay CORS en desarrollo.
    proxy: {
      "/api": {
        target: API_TARGET,
        changeOrigin: true,
      },
    },
  },
});
