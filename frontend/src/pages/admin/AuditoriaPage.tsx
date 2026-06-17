import { useQuery } from "@tanstack/react-query";
import { api } from "../../shared/api/client";
import type { components } from "../../shared/api/schema";

type Entrada = components["schemas"]["AuditoriaEntradaResponse"];

// Etiquetas legibles para las acciones y entidades registradas.
const ACCIONES: Record<string, string> = {
  crear: "Creó",
  editar: "Editó",
  publicar: "Publicó",
  borrar: "Borró",
  restaurar: "Restauró",
  purgar: "Eliminó definitivamente",
  subir_html: "Subió el HTML de",
  crear_paleta: "Creó la paleta",
  editar_paleta: "Editó la paleta",
  borrar_paleta: "Borró la paleta",
  activar_paleta: "Activó la paleta",
};
const ENTIDADES: Record<string, string> = {
  contenido: "contenido",
  usuario: "usuario",
  ciclo: "ciclo",
  curso: "curso",
  asignatura: "asignatura",
  configuracion: "configuración",
};

function accionLegible(e: Entrada): string {
  const verbo = ACCIONES[e.accion] ?? e.accion;
  // Para acciones de paleta/configuracion el verbo ya incluye el objeto.
  if (e.accion.endsWith("_paleta")) return verbo;
  const ent = ENTIDADES[e.entidad] ?? e.entidad;
  return `${verbo} ${ent}`;
}

function fechaLegible(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("es-ES", { dateStyle: "short", timeStyle: "short" });
}

export function AuditoriaPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["auditoria"],
    queryFn: () =>
      api.GET("/api/v1/auditoria", { params: { query: { limite: 200 } } }).then(({ data, error }) => {
        if (error) throw new Error("Error al cargar la auditoría");
        return data!;
      }),
  });

  if (isLoading) return <div className="cms-spinner" role="status" aria-label="Cargando" />;
  if (isError || !data) return <p className="cms-error">No se pudo cargar el registro de auditoría.</p>;

  return (
    <>
      <div className="cms-admin-header">
        <h1 className="cms-h1">Auditoría</h1>
        <span className="cms-muted">{data.total} acciones registradas</span>
      </div>

      {data.entradas.length === 0 ? (
        <p className="cms-empty">Todavía no hay acciones registradas.</p>
      ) : (
        <table className="cms-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Usuario</th>
              <th>Acción</th>
              <th>Detalle</th>
            </tr>
          </thead>
          <tbody>
            {data.entradas.map((e) => (
              <tr key={e.id}>
                <td style={{ whiteSpace: "nowrap" }}>{fechaLegible(e.created_at)}</td>
                <td>
                  {e.usuario_email}
                  <span className="cms-badge" style={{ marginLeft: ".4rem" }}>{e.usuario_rol}</span>
                </td>
                <td>{accionLegible(e)}</td>
                <td className="cms-muted">{e.detalle || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
