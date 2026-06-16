import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import { RequireAuth } from "./auth/RequireAuth";
import { useConfig } from "./config/useConfig";
import { CatalogoPage } from "../pages/CatalogoPage";
import { ContenidoPage } from "../pages/ContenidoPage";
import { LoginPage } from "../pages/LoginPage";
import { DashboardPage } from "../pages/admin/DashboardPage";
import { ContenidosPage } from "../pages/admin/ContenidosPage";
import { ContenidoFormPage } from "../pages/admin/ContenidoFormPage";
import { TaxonomiaPage } from "../pages/admin/TaxonomiaPage";
import { UsuariosPage } from "../pages/admin/UsuariosPage";
import { ConfiguracionPage } from "../pages/admin/ConfiguracionPage";
import { BackupsPage } from "../pages/admin/BackupsPage";
import { PublicLayout } from "../shared/ui/PublicLayout";
import { AdminLayout } from "../shared/ui/AdminLayout";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
});

function AppRoutes() {
  useConfig(); // carga la paleta activa y aplica CSS vars al arrancar

  return (
    <Routes>
      {/* Rutas públicas */}
      <Route element={<PublicLayout />}>
        <Route index element={<CatalogoPage />} />
        <Route path="contenido/:id" element={<ContenidoPage />} />
        <Route path="login" element={<LoginPage />} />
      </Route>

      {/* Rutas protegidas */}
      <Route
        path="admin"
        element={
          <RequireAuth>
            <AdminLayout />
          </RequireAuth>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="contenidos" element={<ContenidosPage />} />
        <Route path="contenidos/nuevo" element={<ContenidoFormPage />} />
        <Route path="contenidos/:id/editar" element={<ContenidoFormPage />} />
        <Route path="taxonomia" element={<TaxonomiaPage />} />
        <Route path="configuracion" element={<ConfiguracionPage />} />
        <Route
          path="usuarios"
          element={
            <RequireAuth rol="admin">
              <UsuariosPage />
            </RequireAuth>
          }
        />
        <Route
          path="copias"
          element={
            <RequireAuth rol="admin">
              <BackupsPage />
            </RequireAuth>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
