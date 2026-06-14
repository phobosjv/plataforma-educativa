import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import DOMPurify from "dompurify";
import { api } from "../shared/api/client";
import type { components } from "../shared/api/schema";

type Contenido = components["schemas"]["ContenidoResponse"];
type Ciclo = components["schemas"]["CicloResponse"];
type Curso = components["schemas"]["CursoResponse"];
type Asignatura = components["schemas"]["AsignaturaResponse"];

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
  const [maximizado, setMaximizado] = useState(false);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["contenido", id],
    queryFn: () => fetchContenido(id!),
    enabled: !!id,
  });

  const esInteractivo = data?.tipo === "interactivo";

  // Taxonomías para construir el "path" del ejercicio (ciclo / curso / asignatura).
  // Comparten queryKey con el catálogo, así que se sirven de la caché de React Query.
  const ciclosQ = useQuery<Ciclo[]>({
    queryKey: ["ciclos"],
    queryFn: () => api.GET("/api/v1/taxonomy/ciclos/").then(({ data }) => data ?? []),
    enabled: esInteractivo,
  });
  const cursosQ = useQuery<Curso[]>({
    queryKey: ["cursos"],
    queryFn: () => api.GET("/api/v1/taxonomy/cursos/").then(({ data }) => data ?? []),
    enabled: esInteractivo,
  });
  const asigQ = useQuery<Asignatura[]>({
    queryKey: ["asignaturas"],
    queryFn: () => api.GET("/api/v1/taxonomy/asignaturas/").then(({ data }) => data ?? []),
    enabled: esInteractivo,
  });

  // Bloquea el scroll del fondo y permite salir con Escape mientras está maximizado.
  useEffect(() => {
    if (!maximizado) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setMaximizado(false);
    };
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = prev;
      window.removeEventListener("keydown", onKey);
    };
  }, [maximizado]);

  if (isLoading) return <div className="cms-spinner" role="status" aria-label="Cargando" />;
  if (isError || !data) return <p className="cms-error">Contenido no encontrado.</p>;

  // path tipo "primaria / 3º / conocimiento del medio / mapa españa"
  const curso = cursosQ.data?.find((c) => c.id === data.curso_id) ?? null;
  const ciclo = ciclosQ.data?.find((c) => c.id === (curso?.ciclo_id ?? data.ciclo_id)) ?? null;
  const asignatura = asigQ.data?.find((a) => a.id === data.asignatura_id) ?? null;
  const pathPartes = [ciclo?.nombre, curso?.nombre, asignatura?.nombre, data.titulo].filter(
    (p): p is string => !!p,
  );
  const pathTexto = pathPartes.join(" / ");

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

      {data.tipo === "interactivo" ? (
        data.sandbox_url ? (
          // El mismo iframe se reutiliza en modo normal y maximizado (no se recarga el
          // ejercicio al cambiar de modo). Aislamiento del ejercicio (CLAUDE.md §10):
          // origen sandbox distinto + sandbox="allow-scripts" SIN allow-same-origin.
          <div
            className={`cms-exercise-wrap${maximizado ? " cms-exercise-wrap--max" : ""}`}
          >
            {maximizado && (
              <div className="cms-exercise-bar">
                <span className="cms-exercise-path" title={pathTexto}>{pathTexto}</span>
                <button
                  type="button"
                  className="cms-btn cms-btn-ghost cms-exercise-min"
                  onClick={() => setMaximizado(false)}
                >
                  ⤡ Minimizar
                </button>
              </div>
            )}
            <iframe
              className="cms-exercise-frame"
              src={data.sandbox_url}
              title={data.titulo}
              sandbox="allow-scripts"
              loading="lazy"
            />
            {!maximizado && (
              <button
                type="button"
                className="cms-btn cms-btn-ghost cms-exercise-max-btn"
                onClick={() => setMaximizado(true)}
                aria-label="Maximizar ejercicio"
              >
                ⤢ Maximizar
              </button>
            )}
          </div>
        ) : (
          <p className="cms-empty">Este ejercicio todavía no tiene fichero.</p>
        )
      ) : data.body_html ? (
        // El HTML ya se saneó en el servidor (nh3); DOMPurify es la 2ª capa
        // en cliente exigida por la sanitización asimétrica (CLAUDE.md §10).
        <div
          className="cms-text cms-prose"
          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(data.body_html) }}
        />
      ) : (
        <p className="cms-empty">Este contenido no tiene cuerpo.</p>
      )}
    </>
  );
}
