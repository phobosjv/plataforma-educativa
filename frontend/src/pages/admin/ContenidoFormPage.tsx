import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../shared/api/client";
import type { components } from "../../shared/api/schema";
import { ContenidoForm, type ContenidoFormValues } from "../../features/content/ContenidoForm";

type Contenido = components["schemas"]["ContenidoResponse"];

function mensajeError(error: unknown): string {
  if (error && typeof error === "object" && "detail" in error) {
    const d = (error as { detail: unknown }).detail;
    if (typeof d === "string") return d;
  }
  return "No se pudo guardar el contenido. Inténtalo de nuevo.";
}

export function ContenidoFormPage() {
  const { id } = useParams<{ id: string }>();
  const modo = id ? "editar" : "crear";
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  // En edición, cargar el contenido para precargar el formulario.
  const { data: existente, isLoading } = useQuery<Contenido>({
    queryKey: ["contenido", id],
    queryFn: () =>
      api
        .GET("/api/v1/contenidos/{contenido_id}", { params: { path: { contenido_id: id! } } })
        .then(({ data, error }) => {
          if (error || !data) throw new Error("No encontrado");
          return data;
        }),
    enabled: modo === "editar",
  });

  function volver() {
    navigate("/admin/contenidos");
  }

  const guardar = useMutation({
    mutationFn: async (v: ContenidoFormValues) => {
      if (modo === "crear") {
        const { data, error } = await api.POST("/api/v1/contenidos/", {
          body: {
            titulo: v.titulo,
            descripcion: v.descripcion,
            tipo: v.tipo,
            idioma: "es",
            etiquetas: v.etiquetas,
            body_html: v.tipo === "texto" ? v.body_html : null,
            ciclo_id: v.ciclo_id,
            curso_id: v.curso_id,
            asignatura_id: v.asignatura_id,
          },
        });
        if (error || !data) throw new Error(mensajeError(error));
        return data;
      }
      const { data, error } = await api.PUT("/api/v1/contenidos/{contenido_id}", {
        params: { path: { contenido_id: id! } },
        body: {
          titulo: v.titulo,
          descripcion: v.descripcion,
          etiquetas: v.etiquetas,
          body_html: v.tipo === "texto" ? v.body_html : null,
          ciclo_id: v.ciclo_id,
          curso_id: v.curso_id,
          asignatura_id: v.asignatura_id,
        },
      });
      if (error || !data) throw new Error(mensajeError(error));
      return data;
    },
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["admin-contenidos"] });
      qc.invalidateQueries({ queryKey: ["contenido", id] });
      // Un interactivo recién creado aún no tiene HTML: ir a su edición para subirlo.
      if (modo === "crear" && data.tipo === "interactivo") {
        navigate(`/admin/contenidos/${data.id}/editar`, { replace: true });
        return;
      }
      volver();
    },
    onError: (e: unknown) => setError(e instanceof Error ? e.message : "Error inesperado."),
  });

  // Subida del fichero HTML de un ejercicio interactivo (multipart; §10).
  const subirHtml = useMutation({
    mutationFn: async (file: File) => {
      const fd = new FormData();
      fd.append("fichero", file);
      const token = localStorage.getItem("auth_token");
      const r = await fetch(`/api/v1/contenidos/${id}/html`, {
        method: "POST",
        body: fd,
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (!r.ok) {
        const cuerpo = await r.json().catch(() => null);
        throw new Error(mensajeError(cuerpo));
      }
      return (await r.json()) as Contenido;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-contenidos"] });
      qc.invalidateQueries({ queryKey: ["contenido", id] });
    },
    onError: (e: unknown) => setError(e instanceof Error ? e.message : "Error inesperado."),
  });

  if (modo === "editar" && isLoading)
    return <div className="cms-spinner" role="status" aria-label="Cargando" />;

  const esInteractivo = existente?.tipo === "interactivo";
  const titulo =
    modo === "crear"
      ? "Nuevo contenido"
      : esInteractivo
        ? "Editar ejercicio interactivo"
        : "Editar artículo";

  return (
    <>
      <div className="cms-admin-header">
        <h1 className="cms-h1">{titulo}</h1>
      </div>

      {error && (
        <div role="alert" className="cms-alert-error" style={{ marginBottom: "1.5rem" }}>
          {error}
        </div>
      )}

      <ContenidoForm
        modo={modo}
        enviando={guardar.isPending}
        inicial={
          existente
            ? {
                titulo: existente.titulo,
                descripcion: existente.descripcion,
                tipo: existente.tipo as "texto" | "interactivo",
                etiquetas: existente.etiquetas,
                body_html: existente.body_html ?? "",
                ciclo_id: existente.ciclo_id ?? null,
                curso_id: existente.curso_id ?? null,
                asignatura_id: existente.asignatura_id ?? null,
              }
            : undefined
        }
        onSubmit={(v) => { setError(null); guardar.mutate(v); }}
        onCancelar={volver}
      />

      {modo === "editar" && esInteractivo && (
        <section className="cms-card" style={{ marginTop: "2rem" }}>
          <h2 className="cms-h2">Fichero HTML del ejercicio</h2>
          <p className="cms-muted">
            Sube el HTML autocontenido del ejercicio. Se ejecuta aislado en un iframe
            sandbox desde un origen distinto; <strong>no se sanea</strong>, así que súbelo
            solo desde fuentes de confianza.
          </p>
          {existente?.hash_html ? (
            <p className="cms-text" style={{ margin: ".5rem 0" }}>
              Fichero actual: <code>{existente.hash_html.slice(0, 12)}…</code>
              {existente.sandbox_url && (
                <>
                  {" — "}
                  <a href={existente.sandbox_url} target="_blank" rel="noreferrer">
                    Previsualizar
                  </a>
                </>
              )}
            </p>
          ) : (
            <p className="cms-muted" style={{ margin: ".5rem 0" }}>
              Todavía no hay ningún fichero subido.
            </p>
          )}
          <input
            type="file"
            accept=".html,text/html"
            disabled={subirHtml.isPending}
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) { setError(null); subirHtml.mutate(file); }
              e.target.value = "";
            }}
          />
          {subirHtml.isPending && (
            <p className="cms-muted" style={{ marginTop: ".5rem" }}>Subiendo…</p>
          )}
        </section>
      )}
    </>
  );
}
