import { Fragment, useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import DOMPurify from "dompurify";
import { api } from "../shared/api/client";
import { useConfig } from "../app/config/useConfig";
import { detectarRed, iconoRedSVG } from "../app/config/redesSociales";
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
  const { nombre_sitio } = useConfig();
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

  // Registra una visita anónima al abrir la ficha del contenido (una por carga). Es
  // "best-effort": el backend solo acumula en memoria y vuelca por lotes; si falla, da igual.
  useEffect(() => {
    if (!data?.id) return;
    api
      .POST("/api/v1/analytics/visitas/{contenido_id}", {
        params: { path: { contenido_id: data.id } },
      })
      .catch(() => {});
  }, [data?.id]);

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

  // Path navegable "primaria › 3º › conocimiento del medio › mapa españa": cada tramo
  // enlaza al catálogo filtrado por esa taxonomía (el título es el tramo actual, sin enlace).
  const curso = cursosQ.data?.find((c) => c.id === data.curso_id) ?? null;
  const ciclo = ciclosQ.data?.find((c) => c.id === (curso?.ciclo_id ?? data.ciclo_id)) ?? null;
  const asignatura = asigQ.data?.find((a) => a.id === data.asignatura_id) ?? null;
  const segmentos: { label: string; to: string | null }[] = [];
  if (ciclo) segmentos.push({ label: ciclo.nombre, to: `/?ciclo=${ciclo.id}` });
  if (curso) segmentos.push({ label: curso.nombre, to: `/?curso=${curso.id}` });
  if (asignatura && curso)
    segmentos.push({
      label: asignatura.nombre,
      to: `/?curso=${curso.id}&asignatura=${asignatura.id}`,
    });
  segmentos.push({ label: data.titulo, to: null });

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
                <Link to="/" className="cms-exercise-home" title="Ir al inicio">
                  {nombre_sitio}
                </Link>
                <nav className="cms-exercise-path" aria-label="Ubicación del ejercicio">
                  {segmentos.map((seg, i) => (
                    <Fragment key={i}>
                      {i > 0 && <span className="cms-exercise-sep" aria-hidden>›</span>}
                      {seg.to ? (
                        <Link to={seg.to} className="cms-exercise-crumb">{seg.label}</Link>
                      ) : (
                        <span className="cms-exercise-crumb cms-exercise-crumb-actual" aria-current="page">
                          {seg.label}
                        </span>
                      )}
                    </Fragment>
                  ))}
                </nav>
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
        <CuerpoArticulo html={data.body_html} />
      ) : (
        <p className="cms-empty">Este contenido no tiene cuerpo.</p>
      )}
    </>
  );
}

// Renderiza el cuerpo de un artículo. El HTML ya se saneó en el servidor (nh3); DOMPurify es la
// 2ª capa en cliente exigida por la sanitización asimétrica (CLAUDE.md §10). Tras montar,
// decora los enlaces: los externos abren en pestaña nueva (rel noopener, §10) y los que apuntan
// a una red social conocida muestran su icono de marca (enlaces a autores/terceros citados).
function CuerpoArticulo({ html }: { html: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const limpio = useMemo(() => DOMPurify.sanitize(html), [html]);

  useEffect(() => {
    const cont = ref.current;
    if (!cont) return;
    cont.querySelectorAll<HTMLAnchorElement>("a[href]").forEach((a) => {
      if (a.hostname && a.hostname !== window.location.hostname) {
        a.target = "_blank";
        a.rel = "noopener noreferrer";
      }
      const red = detectarRed(a.getAttribute("href") ?? "");
      if (!red || a.dataset.redDecorada) return;
      a.dataset.redDecorada = "1";
      a.classList.add("cms-prose-red");
      // El icono se construye en código de confianza (no proviene del HTML del usuario).
      a.insertAdjacentHTML("afterbegin", iconoRedSVG(red));
    });
  }, [limpio]);

  return (
    <div ref={ref} className="cms-text cms-prose" dangerouslySetInnerHTML={{ __html: limpio }} />
  );
}
