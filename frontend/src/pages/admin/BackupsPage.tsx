import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../shared/api/client";
import { useAuth } from "../../app/auth/AuthContext";
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

// Fuerza la descarga de un blob al PC creando un enlace temporal.
function descargarBlob(blob: Blob, nombre: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nombre;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export function BackupsPage() {
  const qc = useQueryClient();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["backups"],
    queryFn: fetchBackups,
  });

  const [error, setError] = useState("");
  const [descargando, setDescargando] = useState<string | null>(null);
  const [exportando, setExportando] = useState(false);

  // Importación / restauración completa (operación destructiva, con confirmación).
  const [importFile, setImportFile] = useState<File | null>(null);
  const [confirmacion, setConfirmacion] = useState("");
  const [importando, setImportando] = useState(false);
  const [importMsg, setImportMsg] = useState("");

  const puedeImportar = !!importFile && confirmacion.trim() === "IMPORTAR" && !importando;

  async function importarTodo() {
    if (!puedeImportar || !importFile) return;
    setError("");
    setImportMsg("");
    setImportando(true);
    try {
      const fd = new FormData();
      fd.append("fichero", importFile);
      fd.append("confirmacion", confirmacion.trim());
      const token = localStorage.getItem("auth_token");
      const r = await fetch("/api/v1/admin/import", {
        method: "POST",
        body: fd,
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      const cuerpo = await r.json().catch(() => null);
      if (!r.ok) {
        setError(cuerpo?.detail ?? "No se pudo importar el archivo.");
        return;
      }
      setImportMsg(
        `Sitio restaurado: ${cuerpo.num_ficheros_media} ficheros de media` +
          (cuerpo.backup_seguridad ? ` (copia previa: ${cuerpo.backup_seguridad})` : "") +
          ". Vas a salir de la sesión; inicia sesión con las credenciales del sitio importado.",
      );
      // La sesión actual puede haber dejado de ser válida (el usuario viene de la BD importada).
      setTimeout(() => {
        logout();
        navigate("/login");
      }, 3500);
    } catch {
      setError("No se pudo importar el archivo.");
    } finally {
      setImportando(false);
    }
  }

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
      descargarBlob(data as Blob, nombre);
    } catch {
      setError("No se pudo descargar la copia de seguridad.");
    } finally {
      setDescargando(null);
    }
  }

  async function exportarTodo() {
    setError("");
    setExportando(true);
    try {
      const { response, data, error: apiError } = await api.POST("/api/v1/admin/export", {
        parseAs: "blob",
      });
      if (apiError || !data) {
        setError("No se pudo generar la exportación completa.");
        return;
      }
      // El nombre del fichero viene en Content-Disposition; si no, uno por defecto.
      const cd = response.headers.get("content-disposition") ?? "";
      const match = cd.match(/filename="?([^"]+)"?/);
      descargarBlob(data as Blob, match?.[1] ?? "plataforma-export.tar.gz");
    } catch {
      setError("No se pudo generar la exportación completa.");
    } finally {
      setExportando(false);
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
        <div style={{ display: "flex", gap: ".5rem", flexWrap: "wrap" }}>
          <button
            className="cms-btn cms-btn-ghost"
            onClick={exportarTodo}
            disabled={exportando}
          >
            {exportando ? "Exportando…" : "Exportar todo (BD + media)"}
          </button>
          <button
            className="cms-btn cms-btn-primary"
            onClick={() => crearBackup.mutate()}
            disabled={crearBackup.isPending}
          >
            {crearBackup.isPending ? "Creando…" : "Crear copia ahora"}
          </button>
        </div>
      </div>

      <p className="cms-text-muted" style={{ marginBottom: "1.5rem" }}>
        La copia de la base de datos se hace automáticamente cada día (junto con una copia
        incremental de los ficheros subidos) y se conservan las más recientes; el contenido en la
        papelera se elimina de forma definitiva tras 30 días. <strong>Exportar todo</strong> descarga
        un archivo único (base de datos + media) con el que puedes <strong>migrar el servidor o
        recuperar el sitio entero</strong> ante un fallo total.
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

      <section className="cms-card" style={{ marginTop: "2.5rem", borderColor: "var(--cms-color-danger)" }}>
        <h2 className="cms-h2">Importar / restaurar el sitio</h2>
        <p className="cms-text-muted">
          Sube un archivo de <strong>«Exportar todo» (.tar.gz)</strong> para restaurar o migrar el sitio
          entero (base de datos + media). Es la operación inversa de la exportación: ideal para poner en
          marcha una web en blanco con el contenido de otra.
        </p>
        <p className="cms-error" style={{ marginTop: ".5rem" }}>
          ⚠️ Operación destructiva: <strong>reemplaza la base de datos actual</strong> y restaura la media.
          Se crea una copia de seguridad automática antes de sobrescribir. Tras importar, deberás iniciar
          sesión con las credenciales del sitio importado.
        </p>

        <div className="cms-form-group" style={{ marginTop: "1rem" }}>
          <label className="cms-label" htmlFor="import-file">Archivo de exportación (.tar.gz)</label>
          <input
            id="import-file"
            type="file"
            accept=".gz,.tgz,application/gzip"
            disabled={importando}
            onChange={(e) => { setImportMsg(""); setImportFile(e.target.files?.[0] ?? null); }}
          />
        </div>

        <div className="cms-form-group">
          <label className="cms-label" htmlFor="import-confirm">
            Escribe <code>IMPORTAR</code> para confirmar
          </label>
          <input
            id="import-confirm"
            className="cms-input"
            value={confirmacion}
            disabled={importando}
            placeholder="IMPORTAR"
            onChange={(e) => setConfirmacion(e.target.value)}
            style={{ maxWidth: "220px" }}
          />
        </div>

        <button
          type="button"
          className="cms-btn cms-btn-primary"
          onClick={importarTodo}
          disabled={!puedeImportar}
        >
          {importando ? "Importando…" : "Importar y reemplazar el sitio"}
        </button>

        {importMsg && (
          <p className="cms-text" role="status" style={{ marginTop: ".75rem", color: "var(--cms-color-primary)" }}>
            {importMsg}
          </p>
        )}
      </section>
    </>
  );
}
