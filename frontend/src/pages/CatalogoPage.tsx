import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../shared/api/client";
import type { components } from "../shared/api/schema";

type Contenido = components["schemas"]["ContenidoResponse"];

function fetchContenidos(): Promise<Contenido[]> {
  return api
    .GET("/api/v1/contenidos/")
    .then(({ data, error }) => {
      if (error) throw new Error("Error al cargar el catálogo");
      return data ?? [];
    });
}

export function CatalogoPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["contenidos-publicos"],
    queryFn: fetchContenidos,
  });

  if (isLoading) return <div className="cms-spinner" role="status" aria-label="Cargando" />;
  if (isError) return <p className="cms-error">No se pudo cargar el catálogo.</p>;

  return (
    <>
      <h1 className="cms-h1" style={{ marginBottom: "1.5rem" }}>Catálogo</h1>
      {!data?.length ? (
        <p className="cms-empty">Aún no hay contenidos publicados.</p>
      ) : (
        <div className="cms-grid">
          {data.map((c) => (
            <Link key={c.id} to={`/contenido/${c.id}`} className="cms-card">
              <span className={`cms-badge cms-badge-${c.tipo}`} style={{ marginBottom: ".5rem" }}>
                {c.tipo}
              </span>
              <p className="cms-h3" style={{ marginTop: ".4rem" }}>{c.titulo}</p>
              {c.descripcion && (
                <p className="cms-muted" style={{ marginTop: ".4rem" }}>{c.descripcion}</p>
              )}
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
