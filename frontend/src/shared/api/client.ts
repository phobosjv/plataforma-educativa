import createClient from "openapi-fetch";
import type { paths } from "./schema";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8001";

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
