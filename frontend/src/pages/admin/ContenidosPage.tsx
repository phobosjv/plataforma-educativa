import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../../shared/api/client";
import type { components } from "../../shared/api/schema";

type Contenido = components["schemas"]["ContenidoResponse"];

function fetchTodos(): Promise<Contenido[]> {
  return api
    .GET("/api/v1/admin/contenidos/")
    .then(({ data, error }) => {
      if (error) throw new Error("Error al cargar");
      return data ?? [];
    });
}

function badgeClass(c: Contenido) {
  if (c.borrado) return "borrado";
  if (c.publicado) return "publicado";
  return "borrador";
}

function estadoLabel(c: Contenido) {
  if (c.borrado) return "papelera";
  if (c.publicado) return "publicado";
  return "borrador";
}

export function ContenidosPage() {
  const qc = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["admin-contenidos"],
    queryFn: fetchTodos,
  });

  const publicar = useMutation({
    mutationFn: (id: string) =>
      api.POST("/api/v1/contenidos/{contenido_id}/publicar", {
        params: { path: { contenido_id: id } },
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-contenidos"] }),
  });

  const borrar = useMutation({
    mutationFn: (id: string) =>
      api.DELETE("/api/v1/contenidos/{contenido_id}", {
        params: { path: { contenido_id: id } },
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-contenidos"] }),
  });

  const restaurar = useMutation({
    mutationFn: (id: string) =>
      api.POST("/api/v1/contenidos/{contenido_id}/restaurar", {
        params: { path: { contenido_id: id } },
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-contenidos"] }),
  });

  const [confirmar, setConfirmar] = useState<string | null>(null);

  if (isLoading) return <div className="cms-spinner" role="status" aria-label="Cargando" />;
  if (isError) return <p className="cms-error">No se pudo cargar la lista de contenidos.</p>;

  return (
    <>
      <div className="cms-admin-header">
        <h1 className="cms-h1">Contenidos</h1>
      </div>
      {!data?.length ? (
        <p className="cms-empty">No hay contenidos creados todavía.</p>
      ) : (
        <table className="cms-table">
          <thead>
            <tr>
              <th>Título</th>
              <th>Tipo</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {data.map((c) => (
              <tr key={c.id}>
                <td>{c.titulo}</td>
                <td>
                  <span className={`cms-badge cms-badge-${c.tipo}`}>{c.tipo}</span>
                </td>
                <td>
                  <span className={`cms-badge cms-badge-${badgeClass(c)}`}>
                    {estadoLabel(c)}
                  </span>
                </td>
                <td style={{ display: "flex", gap: ".4rem", flexWrap: "wrap" }}>
                  {!c.publicado && !c.borrado && (
                    <button
                      className="cms-btn cms-btn-primary"
                      onClick={() => publicar.mutate(c.id)}
                    >
                      Publicar
                    </button>
                  )}
                  {c.borrado ? (
                    <button
                      className="cms-btn cms-btn-ghost"
                      onClick={() => restaurar.mutate(c.id)}
                    >
                      Restaurar
                    </button>
                  ) : (
                    confirmar === c.id ? (
                      <>
                        <button
                          className="cms-btn cms-btn-danger"
                          onClick={() => { borrar.mutate(c.id); setConfirmar(null); }}
                        >
                          Confirmar borrado
                        </button>
                        <button
                          className="cms-btn cms-btn-ghost"
                          onClick={() => setConfirmar(null)}
                        >
                          Cancelar
                        </button>
                      </>
                    ) : (
                      <button
                        className="cms-btn cms-btn-ghost"
                        onClick={() => setConfirmar(c.id)}
                      >
                        Borrar
                      </button>
                    )
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
