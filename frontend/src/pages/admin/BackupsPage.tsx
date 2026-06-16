import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../../shared/api/client";
import type { components } from "../../shared/api/schema";

type Backup = components["schemas"]["BackupResponse"];

function fetchBackups(): Promise<Backup[]> {
  return api.GET("/api/v1/admin/backups").then(({ data, error }) => {
    if (error) throw new Error("Sin acceso");
    return data ?? [];
  });
}

function formatoTamano(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} KB`;
  return `${(kb / 1024).toFixed(1)} MB`;
}

function formatoFecha(iso: string): string {
  return new Date(iso).toLocaleString("es-ES", { dateStyle: "medium", timeStyle: "short" });
}

export function BackupsPage() {
  const qc = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["backups"],
    queryFn: fetchBackups,
  });

  const [error, setError] = useState("");
  const [descargando, setDescargando] = useState<string | null>(null);

  async function descargar(nombre: string) {
    setError("");
    setDescargando(nombre);
    try {
      const { data, error: apiError } = await api.GET("/api/v1/admin/backups/{nombre}", {
        params: { path: { nombre } },
        parseAs: "blob",
      });
      if (apiError || !data) {
        setError("No se pudo descargar la copia de seguridad.");
        return;
      }
      // Forzar la descarga al PC creando un enlace temporal hacia el blob.
      const url = URL.createObjectURL(data as Blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = nombre;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      setError("No se pudo descargar la copia de seguridad.");
    } finally {
      setDescargando(null);
    }
  }

  const crearBackup = useMutation({
    mutationFn: () => api.POST("/api/v1/admin/backups"),
    onSuccess: ({ error: apiError }) => {
      if (apiError) {
        setError("No se pudo crear la copia de seguridad.");
        return;
      }
      setError("");
      qc.invalidateQueries({ queryKey: ["backups"] });
    },
    onError: () => setError("No se pudo crear la copia de seguridad."),
  });

  return (
    <>
      <div className="cms-admin-header">
        <h1 className="cms-h1">Copias de seguridad</h1>
        <button
          className="cms-btn cms-btn-primary"
          onClick={() => crearBackup.mutate()}
          disabled={crearBackup.isPending}
        >
          {crearBackup.isPending ? "Creando…" : "Crear copia ahora"}
        </button>
      </div>

      <p className="cms-text-muted" style={{ marginBottom: "1.5rem" }}>
        La copia de la base de datos se hace automáticamente cada día y se conservan las más
        recientes; el contenido en la papelera se elimina de forma definitiva tras 30 días.
        También puedes crear una copia manual cuando lo necesites.
      </p>

      {error && <p className="cms-error">{error}</p>}

      {isLoading ? (
        <div className="cms-spinner" role="status" aria-label="Cargando" />
      ) : isError ? (
        <p className="cms-error">No tienes permisos para ver las copias de seguridad.</p>
      ) : data && data.length > 0 ? (
        <table className="cms-table">
          <thead>
            <tr>
              <th>Copia</th>
              <th>Tamaño</th>
              <th>Fecha</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {data.map((b) => (
              <tr key={b.nombre}>
                <td>{b.nombre}</td>
                <td>{formatoTamano(b.tamano_bytes)}</td>
                <td>{formatoFecha(b.creado_en)}</td>
                <td>
                  <button
                    className="cms-btn cms-btn-ghost"
                    onClick={() => descargar(b.nombre)}
                    disabled={descargando === b.nombre}
                  >
                    {descargando === b.nombre ? "Descargando…" : "Descargar"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="cms-text-muted">Aún no hay copias de seguridad.</p>
      )}
    </>
  );
}
