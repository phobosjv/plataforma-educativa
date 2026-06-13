import createClient from "openapi-fetch";
import type { paths } from "./schema";

// Por defecto, baseUrl vacío => peticiones relativas al mismo origen
// (localhost:5173), que el proxy de Vite reenvía al backend. Así no hay CORS
// en desarrollo. En producción se sirve tras el mismo dominio/proxy inverso.
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export const api = createClient<paths>({ baseUrl: BASE_URL });

api.use({
  onRequest({ request }) {
    const token = localStorage.getItem("auth_token");
    if (token) {
      request.headers.set("Authorization", `Bearer ${token}`);
    }
    return request;
  },
});
