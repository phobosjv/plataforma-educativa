import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { api } from "../shared/api/client";
import type { components } from "../shared/api/schema";

type Contenido = components["schemas"]["ContenidoResponse"];

const SANDBOX_ORIGIN = import.meta.env.VITE_SANDBOX_ORIGIN ?? "http://sandbox.localhost:8001";

function fetchContenido(id: string): Promise<Contenido> {
  return api
    .GET("/api/v1/contenidos/{contenido_id}", { params: { path: { contenido_id: id } } })
    .then(({ data, error }) => {
      if (error) throw new Error("No encontrado");
      return data!;
    });
}

export function ContenidoPage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["contenido", id],
    queryFn: () => fetchContenido(id!),
    enabled: !!id,
  });

  if (isLoading) return <div className="cms-spinner" role="status" aria-label="Cargando" />;
  if (isError || !data) return <p className="cms-error">Contenido no encontrado.</p>;

  return (
    <>
      <p className="cms-muted" style={{ marginBottom: ".5rem" }}>
        <span className={`cms-badge cms-badge-${data.tipo}`}>{data.tipo}</span>
        {data.etiquetas.length > 0 && (
          <span style={{ marginLeft: ".5rem" }}>{data.etiquetas.join(", ")}</span>
        )}
      </p>
      <h1 className="cms-h1" style={{ marginBottom: "1rem" }}>{data.titulo}</h1>
      {data.descripcion && (
        <p className="cms-text cms-muted" style={{ marginBottom: "1.5rem" }}>{data.descripcion}</p>
      )}

      {data.tipo === "interactivo" && data.hash_html ? (
        <iframe
          className="cms-exercise-frame"
          src={`${SANDBOX_ORIGIN}/ejercicio/${data.hash_html}`}
          title={data.titulo}
          sandbox="allow-scripts"
          loading="lazy"
        />
      ) : data.body_html ? (
        <div
          className="cms-text"
          dangerouslySetInnerHTML={{ __html: data.body_html }}
        />
      ) : (
        <p className="cms-empty">Este contenido no tiene cuerpo.</p>
      )}
    </>
  );
}
