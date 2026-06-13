import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useAuth } from "../../app/auth/AuthContext";
import { api } from "../../shared/api/client";

function fetchResumen() {
  return Promise.all([
    api.GET("/api/v1/admin/contenidos/").then(({ data }) => data ?? []),
    api.GET("/api/v1/taxonomy/ciclos/").then(({ data }) => data ?? []),
  ]);
}

export function DashboardPage() {
  const { user } = useAuth();
  const { data, isLoading } = useQuery({
    queryKey: ["admin-resumen"],
    queryFn: fetchResumen,
  });

  const [contenidos, ciclos] = data ?? [[], []];

  return (
    <>
      <div className="cms-admin-header">
        <h1 className="cms-h1">Inicio</h1>
        <span className="cms-muted">Rol: {user?.rol}</span>
      </div>

      {isLoading ? (
        <div className="cms-spinner" role="status" aria-label="Cargando" />
      ) : (
        <div className="cms-grid" style={{ maxWidth: 600 }}>
          <Link to="/admin/contenidos" className="cms-card">
            <p className="cms-muted">Contenidos totales</p>
            <p className="cms-h2" style={{ marginTop: ".25rem" }}>{contenidos.length}</p>
          </Link>
          <Link to="/admin/taxonomia" className="cms-card">
            <p className="cms-muted">Ciclos educativos</p>
            <p className="cms-h2" style={{ marginTop: ".25rem" }}>{ciclos.length}</p>
          </Link>
        </div>
      )}
    </>
  );
}
