import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../shared/api/client";
import type { components } from "../../shared/api/schema";
import { RichTextEditor } from "./RichTextEditor";

type Ciclo = components["schemas"]["CicloResponse"];
type Curso = components["schemas"]["CursoResponse"];
type Asignatura = components["schemas"]["AsignaturaResponse"];

export type TipoContenido = "texto" | "interactivo" | "pdf";

export interface ContenidoFormValues {
  titulo: string;
  descripcion: string;
  tipo: TipoContenido;
  etiquetas: string[];
  body_html: string;
  ciclo_id: string | null;
  curso_id: string | null;
  asignatura_id: string | null;
  es_examen: boolean;
}

const VACIO: ContenidoFormValues = {
  titulo: "",
  descripcion: "",
  tipo: "texto",
  etiquetas: [],
  body_html: "",
  ciclo_id: null,
  curso_id: null,
  asignatura_id: null,
  es_examen: false,
};

export function ContenidoForm({
  modo,
  inicial,
  enviando,
  onSubmit,
  onCancelar,
}: {
  modo: "crear" | "editar";
  inicial?: Partial<ContenidoFormValues>;
  enviando: boolean;
  onSubmit: (v: ContenidoFormValues) => void;
  onCancelar: () => void;
}) {
  const [v, setV] = useState<ContenidoFormValues>({ ...VACIO, ...inicial });
  const [etiquetasTexto, setEtiquetasTexto] = useState((inicial?.etiquetas ?? []).join(", "));

  // La clasificación puede asignarse y editarse en ambos modos (crear y editar).
  const { data: ciclos = [] } = useQuery<Ciclo[]>({
    queryKey: ["ciclos"],
    queryFn: () => api.GET("/api/v1/taxonomy/ciclos/").then(({ data }) => data ?? []),
  });
  const { data: cursos = [] } = useQuery<Curso[]>({
    queryKey: ["cursos"],
    queryFn: () => api.GET("/api/v1/taxonomy/cursos/").then(({ data }) => data ?? []),
  });
  const { data: asignaturas = [] } = useQuery<Asignatura[]>({
    queryKey: ["asignaturas"],
    queryFn: () => api.GET("/api/v1/taxonomy/asignaturas/").then(({ data }) => data ?? []),
  });

  const cursosDelCiclo = v.ciclo_id ? cursos.filter((c) => c.ciclo_id === v.ciclo_id) : cursos;
  const asignaturasNormales = asignaturas.filter((a) => !a.transversal);
  const asignaturasTransversales = asignaturas.filter((a) => a.transversal);
  const asignaturaActual = asignaturas.find((a) => a.id === v.asignatura_id) ?? null;
  const esTransversal = !!asignaturaActual?.transversal;

  function set<K extends keyof ContenidoFormValues>(k: K, val: ContenidoFormValues[K]) {
    setV((prev) => ({ ...prev, [k]: val }));
  }

  // Al elegir asignatura: si es transversal, se desclasifica de ciclo/curso (no aplican).
  function setAsignatura(id: string | null) {
    const transversal = !!asignaturas.find((a) => a.id === id)?.transversal;
    setV((prev) => ({
      ...prev,
      asignatura_id: id,
      ciclo_id: transversal ? null : prev.ciclo_id,
      curso_id: transversal ? null : prev.curso_id,
    }));
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const etiquetas = etiquetasTexto
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    // Una asignatura transversal nunca lleva ciclo/curso (se agrupa en Aula Abierta).
    const taxonomia = esTransversal
      ? { ciclo_id: null, curso_id: null }
      : { ciclo_id: v.ciclo_id, curso_id: v.curso_id };
    // "Examen" solo aplica a interactivos: nunca lo enviamos en un artículo de texto.
    const es_examen = v.tipo === "interactivo" ? v.es_examen : false;
    onSubmit({ ...v, ...taxonomia, titulo: v.titulo.trim(), etiquetas, es_examen });
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="cms-form-group">
        <label className="cms-label" htmlFor="c-titulo">Título</label>
        <input
          id="c-titulo"
          className="cms-input"
          value={v.titulo}
          maxLength={500}
          onChange={(e) => set("titulo", e.target.value)}
          placeholder="Los animales del bosque"
          required
        />
      </div>

      {modo === "crear" && (
        <div className="cms-form-group">
          <label className="cms-label" htmlFor="c-tipo">Tipo de contenido</label>
          <select
            id="c-tipo"
            className="cms-select"
            value={v.tipo}
            onChange={(e) => set("tipo", e.target.value as TipoContenido)}
          >
            <option value="texto">Artículo de texto</option>
            <option value="interactivo">Ejercicio interactivo (HTML)</option>
            <option value="pdf">Ficha PDF (imprimible)</option>
          </select>
          {v.tipo === "interactivo" && (
            <p className="cms-muted" style={{ marginTop: ".4rem" }}>
              Tras crearlo podrás subir el fichero HTML del ejercicio desde la edición.
            </p>
          )}
          {v.tipo === "pdf" && (
            <p className="cms-muted" style={{ marginTop: ".4rem" }}>
              Tras crearla podrás subir el fichero PDF de la ficha desde la edición.
            </p>
          )}
        </div>
      )}

      <div className="cms-form-group">
        <label className="cms-label" htmlFor="c-desc">Descripción breve</label>
        <input
          id="c-desc"
          className="cms-input"
          value={v.descripcion}
          onChange={(e) => set("descripcion", e.target.value)}
          placeholder="Un resumen de una línea (opcional)"
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1rem" }}>
          {!esTransversal && (
            <>
              <div className="cms-form-group">
                <label className="cms-label" htmlFor="c-ciclo">Ciclo</label>
                <select
                  id="c-ciclo"
                  className="cms-select"
                  value={v.ciclo_id ?? ""}
                  onChange={(e) => { set("ciclo_id", e.target.value || null); set("curso_id", null); }}
                >
                  <option value="">— Sin asignar —</option>
                  {ciclos.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                </select>
              </div>
              <div className="cms-form-group">
                <label className="cms-label" htmlFor="c-curso">Curso</label>
                <select
                  id="c-curso"
                  className="cms-select"
                  value={v.curso_id ?? ""}
                  onChange={(e) => set("curso_id", e.target.value || null)}
                >
                  <option value="">— Sin asignar —</option>
                  {cursosDelCiclo.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                </select>
              </div>
            </>
          )}
          <div className="cms-form-group">
            <label className="cms-label" htmlFor="c-asig">Asignatura</label>
            <select
              id="c-asig"
              className="cms-select"
              value={v.asignatura_id ?? ""}
              onChange={(e) => setAsignatura(e.target.value || null)}
            >
              <option value="">— Sin asignar —</option>
              {asignaturasNormales.length > 0 && (
                <optgroup label="Asignaturas">
                  {asignaturasNormales.map((a) => <option key={a.id} value={a.id}>{a.nombre}</option>)}
                </optgroup>
              )}
              {asignaturasTransversales.length > 0 && (
                <optgroup label="Transversales (Aula Abierta)">
                  {asignaturasTransversales.map((a) => <option key={a.id} value={a.id}>{a.nombre}</option>)}
                </optgroup>
              )}
            </select>
          </div>
      </div>
      {esTransversal && (
        <p className="cms-muted" style={{ marginTop: "-.5rem", marginBottom: "1rem" }}>
          Asignatura transversal: este contenido no se clasifica por ciclo ni curso; aparecerá en
          «Aula Abierta».
        </p>
      )}

      <div className="cms-form-group">
        <label className="cms-label" htmlFor="c-tags">Etiquetas</label>
        <input
          id="c-tags"
          className="cms-input"
          value={etiquetasTexto}
          onChange={(e) => setEtiquetasTexto(e.target.value)}
          placeholder="bosque, animales, otoño (separadas por comas)"
        />
      </div>

      {v.tipo === "interactivo" && (
        <div className="cms-form-group">
          <label className="cms-label" style={{ display: "flex", alignItems: "center", gap: ".5rem", cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={v.es_examen}
              onChange={(e) => set("es_examen", e.target.checked)}
            />
            Examen (simulacro)
          </label>
          <p className="cms-muted" style={{ marginTop: ".3rem" }}>
            Márcalo si este ejercicio es una simulación de examen. En el catálogo aparecerá al final
            de la lista y con un icono distinto.
          </p>
        </div>
      )}

      {v.tipo === "texto" && (
        <div className="cms-form-group">
          <label className="cms-label">Cuerpo del artículo</label>
          <RichTextEditor value={v.body_html} onChange={(html) => set("body_html", html)} />
          <p className="cms-muted" style={{ marginTop: ".4rem" }}>
            El contenido se sanea automáticamente al guardar por seguridad.
          </p>
        </div>
      )}

      <div style={{ display: "flex", gap: ".5rem", marginTop: "1rem" }}>
        <button type="submit" className="cms-btn cms-btn-primary" disabled={enviando || !v.titulo.trim()}>
          {enviando
            ? "Guardando…"
            : modo === "crear"
              ? v.tipo === "interactivo"
                ? "Crear ejercicio"
                : v.tipo === "pdf"
                  ? "Crear ficha PDF"
                  : "Crear artículo"
              : "Guardar cambios"}
        </button>
        <button type="button" className="cms-btn cms-btn-ghost" onClick={onCancelar}>
          Cancelar
        </button>
      </div>
    </form>
  );
}
