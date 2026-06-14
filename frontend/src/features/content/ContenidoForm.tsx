import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../shared/api/client";
import type { components } from "../../shared/api/schema";
import { RichTextEditor } from "./RichTextEditor";

type Ciclo = components["schemas"]["CicloResponse"];
type Curso = components["schemas"]["CursoResponse"];
type Asignatura = components["schemas"]["AsignaturaResponse"];

export type TipoContenido = "texto" | "interactivo";

export interface ContenidoFormValues {
  titulo: string;
  descripcion: string;
  tipo: TipoContenido;
  etiquetas: string[];
  body_html: string;
  ciclo_id: string | null;
  curso_id: string | null;
  asignatura_id: string | null;
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

  function set<K extends keyof ContenidoFormValues>(k: K, val: ContenidoFormValues[K]) {
    setV((prev) => ({ ...prev, [k]: val }));
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const etiquetas = etiquetasTexto
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    onSubmit({ ...v, titulo: v.titulo.trim(), etiquetas });
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
          </select>
          {v.tipo === "interactivo" && (
            <p className="cms-muted" style={{ marginTop: ".4rem" }}>
              Tras crearlo podrás subir el fichero HTML del ejercicio desde la edición.
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
          <div className="cms-form-group">
            <label className="cms-label" htmlFor="c-asig">Asignatura</label>
            <select
              id="c-asig"
              className="cms-select"
              value={v.asignatura_id ?? ""}
              onChange={(e) => set("asignatura_id", e.target.value || null)}
            >
              <option value="">— Sin asignar —</option>
              {asignaturas.map((a) => <option key={a.id} value={a.id}>{a.nombre}</option>)}
            </select>
          </div>
      </div>

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
