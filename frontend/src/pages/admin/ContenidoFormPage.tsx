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
            tipo: "texto",
            idioma: "es",
            etiquetas: v.etiquetas,
            body_html: v.body_html,
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
          body_html: v.body_html,
        },
      });
      if (error || !data) throw new Error(mensajeError(error));
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-contenidos"] });
      qc.invalidateQueries({ queryKey: ["contenido", id] });
      volver();
    },
    onError: (e: unknown) => setError(e instanceof Error ? e.message : "Error inesperado."),
  });

  if (modo === "editar" && isLoading)
    return <div className="cms-spinner" role="status" aria-label="Cargando" />;

  return (
    <>
      <div className="cms-admin-header">
        <h1 className="cms-h1">{modo === "crear" ? "Nuevo artículo" : "Editar artículo"}</h1>
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
                etiquetas: existente.etiquetas,
                body_html: existente.body_html ?? "",
              }
            : undefined
        }
        onSubmit={(v) => { setError(null); guardar.mutate(v); }}
        onCancelar={volver}
      />
    </>
  );
}
