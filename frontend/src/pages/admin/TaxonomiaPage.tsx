import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { api } from "../../shared/api/client";
import type { components } from "../../shared/api/schema";

type Ciclo = components["schemas"]["CicloResponse"];
type Curso = components["schemas"]["CursoResponse"];
type Asignatura = components["schemas"]["AsignaturaResponse"];

// ── Hooks de datos ────────────────────────────────────────────────────────────

function useCiclos() {
  return useQuery<Ciclo[]>({
    queryKey: ["ciclos"],
    queryFn: () => api.GET("/api/v1/taxonomy/ciclos/").then(({ data }) => data ?? []),
  });
}

function useCursos() {
  return useQuery<Curso[]>({
    queryKey: ["cursos"],
    queryFn: () => api.GET("/api/v1/taxonomy/cursos/").then(({ data }) => data ?? []),
  });
}

function useAsignaturas() {
  return useQuery<Asignatura[]>({
    queryKey: ["asignaturas"],
    queryFn: () => api.GET("/api/v1/taxonomy/asignaturas/").then(({ data }) => data ?? []),
  });
}

// ── Componente de fila editable ───────────────────────────────────────────────

interface FilaProps {
  nombre: string;
  extra?: React.ReactNode;
  onEdit: (nombre: string) => void;
  onDelete: () => void;
}

function FilaEditable({ nombre, extra, onEdit, onDelete }: FilaProps) {
  const [editando, setEditando] = useState(false);
  const [valor, setValor] = useState(nombre);
  const [confirmando, setConfirmando] = useState(false);

  function guardar() {
    if (valor.trim() && valor.trim() !== nombre) onEdit(valor.trim());
    setEditando(false);
  }

  return (
    <tr>
      <td>
        {editando ? (
          <input
            className="cms-input"
            style={{ padding: ".3rem .5rem" }}
            value={valor}
            onChange={(e) => setValor(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") guardar(); if (e.key === "Escape") setEditando(false); }}
            autoFocus
          />
        ) : (
          nombre
        )}
      </td>
      {extra && <td>{extra}</td>}
      <td style={{ display: "flex", gap: ".4rem", flexWrap: "wrap" }}>
        {editando ? (
          <>
            <button className="cms-btn cms-btn-primary" onClick={guardar}>Guardar</button>
            <button className="cms-btn cms-btn-ghost" onClick={() => { setValor(nombre); setEditando(false); }}>Cancelar</button>
          </>
        ) : confirmando ? (
          <>
            <button className="cms-btn cms-btn-danger" onClick={() => { onDelete(); setConfirmando(false); }}>Confirmar</button>
            <button className="cms-btn cms-btn-ghost" onClick={() => setConfirmando(false)}>Cancelar</button>
          </>
        ) : (
          <>
            <button className="cms-btn cms-btn-ghost" onClick={() => setEditando(true)}>Editar</button>
            <button className="cms-btn cms-btn-ghost" onClick={() => setConfirmando(true)}>Borrar</button>
          </>
        )}
      </td>
    </tr>
  );
}

// ── Página principal ──────────────────────────────────────────────────────────

export function TaxonomiaPage() {
  const qc = useQueryClient();

  const { data: ciclos, isLoading: loadCiclos } = useCiclos();
  const { data: cursos, isLoading: loadCursos } = useCursos();
  const { data: asignaturas, isLoading: loadAsig } = useAsignaturas();

  // Ciclos
  const crearCiclo = useMutation({
    mutationFn: (body: components["schemas"]["CrearCicloRequest"]) =>
      api.POST("/api/v1/taxonomy/ciclos/", { body }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["ciclos"] }); setNombreCiclo(""); },
  });
  const editarCiclo = useMutation({
    mutationFn: ({ id, body }: { id: string; body: components["schemas"]["ActualizarCicloRequest"] }) =>
      api.PUT("/api/v1/taxonomy/ciclos/{ciclo_id}", { params: { path: { ciclo_id: id } }, body }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["ciclos"] }),
  });
  const borrarCiclo = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await api.DELETE("/api/v1/taxonomy/ciclos/{ciclo_id}", { params: { path: { ciclo_id: id } } });
      if (error) throw new Error((error as { detail?: string })?.detail ?? "No se pudo eliminar el ciclo.");
    },
    onSuccess: () => { setError(""); qc.invalidateQueries({ queryKey: ["ciclos"] }); qc.invalidateQueries({ queryKey: ["cursos"] }); },
    onError: (e: unknown) => setError(e instanceof Error ? e.message : "No se pudo eliminar el ciclo."),
  });

  // Cursos
  const crearCurso = useMutation({
    mutationFn: (body: components["schemas"]["CrearCursoRequest"]) =>
      api.POST("/api/v1/taxonomy/cursos/", { body }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["cursos"] }); setNombreCurso(""); },
  });
  const editarCurso = useMutation({
    mutationFn: ({ id, body }: { id: string; body: components["schemas"]["ActualizarCursoRequest"] }) =>
      api.PUT("/api/v1/taxonomy/cursos/{curso_id}", { params: { path: { curso_id: id } }, body }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["cursos"] }),
  });
  const borrarCurso = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await api.DELETE("/api/v1/taxonomy/cursos/{curso_id}", { params: { path: { curso_id: id } } });
      if (error) throw new Error((error as { detail?: string })?.detail ?? "No se pudo eliminar el curso.");
    },
    onSuccess: () => { setError(""); qc.invalidateQueries({ queryKey: ["cursos"] }); },
    onError: (e: unknown) => setError(e instanceof Error ? e.message : "No se pudo eliminar el curso."),
  });

  // Asignaturas
  const crearAsig = useMutation({
    mutationFn: (body: components["schemas"]["CrearAsignaturaRequest"]) =>
      api.POST("/api/v1/taxonomy/asignaturas/", { body }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["asignaturas"] });
      setNombreAsig("");
      setTransversalAsig(false);
    },
  });
  const editarAsig = useMutation({
    mutationFn: ({ id, body }: { id: string; body: components["schemas"]["ActualizarAsignaturaRequest"] }) =>
      api.PUT("/api/v1/taxonomy/asignaturas/{asignatura_id}", { params: { path: { asignatura_id: id } }, body }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["asignaturas"] }),
  });
  const borrarAsig = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await api.DELETE("/api/v1/taxonomy/asignaturas/{asignatura_id}", { params: { path: { asignatura_id: id } } });
      if (error) throw new Error((error as { detail?: string })?.detail ?? "No se pudo eliminar la asignatura.");
    },
    onSuccess: () => { setError(""); qc.invalidateQueries({ queryKey: ["asignaturas"] }); },
    onError: (e: unknown) => setError(e instanceof Error ? e.message : "No se pudo eliminar la asignatura."),
  });

  const [error, setError] = useState("");
  const [nombreCiclo, setNombreCiclo] = useState("");
  const [nombreCurso, setNombreCurso] = useState("");
  const [cicloSeleccionado, setCicloSeleccionado] = useState("");
  const [nombreAsig, setNombreAsig] = useState("");
  const [colorAsig, setColorAsig] = useState("#6366f1");
  const [transversalAsig, setTransversalAsig] = useState(false);

  function handleCiclo(e: FormEvent) {
    e.preventDefault();
    if (!nombreCiclo.trim()) return;
    crearCiclo.mutate({ nombre: nombreCiclo, orden: (ciclos?.length ?? 0) + 1 });
  }

  function handleCurso(e: FormEvent) {
    e.preventDefault();
    if (!nombreCurso.trim() || !cicloSeleccionado) return;
    crearCurso.mutate({
      nombre: nombreCurso,
      ciclo_id: cicloSeleccionado,
      orden: (cursos?.filter((c) => c.ciclo_id === cicloSeleccionado).length ?? 0) + 1,
    });
  }

  function handleAsig(e: FormEvent) {
    e.preventDefault();
    if (!nombreAsig.trim()) return;
    crearAsig.mutate({ nombre: nombreAsig, color: colorAsig, transversal: transversalAsig });
  }

  return (
    <>
      <div className="cms-admin-header">
        <h1 className="cms-h1">Taxonomía</h1>
      </div>

      {error && (
        <p className="cms-error" role="alert" style={{ marginBottom: "1.5rem" }}>{error}</p>
      )}

      {/* ── Ciclos ── */}
      <section style={{ marginBottom: "2.5rem" }}>
        <h2 className="cms-h2" style={{ marginBottom: ".75rem" }}>Ciclos educativos</h2>
        {loadCiclos ? (
          <div className="cms-spinner" role="status" aria-label="Cargando" />
        ) : !ciclos?.length ? (
          <p className="cms-empty">Sin ciclos aún.</p>
        ) : (
          <table className="cms-table" style={{ marginBottom: "1rem" }}>
            <thead><tr><th>Nombre</th><th>Acciones</th></tr></thead>
            <tbody>
              {ciclos.map((c) => (
                <FilaEditable
                  key={c.id}
                  nombre={c.nombre}
                  onEdit={(nombre) => editarCiclo.mutate({ id: c.id, body: { nombre } })}
                  onDelete={() => borrarCiclo.mutate(c.id)}
                />
              ))}
            </tbody>
          </table>
        )}
        <form onSubmit={handleCiclo} style={{ display: "flex", gap: ".5rem", alignItems: "flex-end" }}>
          <div className="cms-form-group" style={{ marginBottom: 0, flex: 1 }}>
            <label className="cms-label" htmlFor="nuevo-ciclo">Nuevo ciclo</label>
            <input id="nuevo-ciclo" className="cms-input" value={nombreCiclo}
              onChange={(e) => setNombreCiclo(e.target.value)} placeholder="Ej. Educación Primaria" />
          </div>
          <button type="submit" className="cms-btn cms-btn-primary" style={{ alignSelf: "flex-end" }}>Añadir</button>
        </form>
      </section>

      {/* ── Cursos ── */}
      <section style={{ marginBottom: "2.5rem" }}>
        <h2 className="cms-h2" style={{ marginBottom: ".75rem" }}>Cursos</h2>
        {loadCursos ? (
          <div className="cms-spinner" role="status" aria-label="Cargando" />
        ) : !cursos?.length ? (
          <p className="cms-empty">Sin cursos aún.</p>
        ) : (
          <table className="cms-table" style={{ marginBottom: "1rem" }}>
            <thead><tr><th>Nombre</th><th>Ciclo</th><th>Acciones</th></tr></thead>
            <tbody>
              {cursos.map((c) => (
                <FilaEditable
                  key={c.id}
                  nombre={c.nombre}
                  extra={<span className="cms-muted">{ciclos?.find((ci) => ci.id === c.ciclo_id)?.nombre ?? "—"}</span>}
                  onEdit={(nombre) => editarCurso.mutate({ id: c.id, body: { nombre } })}
                  onDelete={() => borrarCurso.mutate(c.id)}
                />
              ))}
            </tbody>
          </table>
        )}
        <form onSubmit={handleCurso} style={{ display: "flex", gap: ".5rem", alignItems: "flex-end", flexWrap: "wrap" }}>
          <div className="cms-form-group" style={{ marginBottom: 0, flex: "0 0 180px" }}>
            <label className="cms-label" htmlFor="ciclo-sel">Ciclo</label>
            <select id="ciclo-sel" className="cms-select" value={cicloSeleccionado}
              onChange={(e) => setCicloSeleccionado(e.target.value)}>
              <option value="">— Selecciona —</option>
              {ciclos?.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
            </select>
          </div>
          <div className="cms-form-group" style={{ marginBottom: 0, flex: 1 }}>
            <label className="cms-label" htmlFor="nuevo-curso">Nuevo curso</label>
            <input id="nuevo-curso" className="cms-input" value={nombreCurso}
              onChange={(e) => setNombreCurso(e.target.value)} placeholder="Ej. 1º Primaria" />
          </div>
          <button type="submit" className="cms-btn cms-btn-primary" style={{ alignSelf: "flex-end" }}>Añadir</button>
        </form>
      </section>

      {/* ── Asignaturas ── */}
      <section>
        <h2 className="cms-h2" style={{ marginBottom: ".75rem" }}>Asignaturas</h2>
        {loadAsig ? (
          <div className="cms-spinner" role="status" aria-label="Cargando" />
        ) : !asignaturas?.length ? (
          <p className="cms-empty">Sin asignaturas aún.</p>
        ) : (
          <table className="cms-table" style={{ marginBottom: "1rem" }}>
            <thead><tr><th>Nombre</th><th>Color / Tipo</th><th>Acciones</th></tr></thead>
            <tbody>
              {asignaturas.map((a) => (
                <FilaEditable
                  key={a.id}
                  nombre={a.nombre}
                  extra={
                    <span style={{ display: "inline-flex", alignItems: "center", gap: ".5rem", flexWrap: "wrap" }}>
                      <span style={{ display: "inline-flex", alignItems: "center", gap: ".4rem" }}>
                        <span style={{ width: 16, height: 16, borderRadius: "50%", background: a.color, display: "inline-block", border: "1px solid #ccc" }} />
                        {a.color}
                      </span>
                      {a.transversal && <span className="cms-badge cms-badge-publicado">Transversal</span>}
                      <button
                        type="button"
                        className="cms-btn cms-btn-ghost"
                        style={{ padding: ".2rem .5rem", fontSize: ".8rem" }}
                        onClick={() => editarAsig.mutate({ id: a.id, body: { transversal: !a.transversal } })}
                      >
                        {a.transversal ? "Quitar transversal" : "Marcar transversal"}
                      </button>
                    </span>
                  }
                  onEdit={(nombre) => editarAsig.mutate({ id: a.id, body: { nombre } })}
                  onDelete={() => borrarAsig.mutate(a.id)}
                />
              ))}
            </tbody>
          </table>
        )}
        <form onSubmit={handleAsig} style={{ display: "flex", gap: ".5rem", alignItems: "flex-end", flexWrap: "wrap" }}>
          <div className="cms-form-group" style={{ marginBottom: 0, flex: 1 }}>
            <label className="cms-label" htmlFor="nueva-asig">Nueva asignatura</label>
            <input id="nueva-asig" className="cms-input" value={nombreAsig}
              onChange={(e) => setNombreAsig(e.target.value)} placeholder="Ej. Matemáticas" />
          </div>
          <div className="cms-form-group" style={{ marginBottom: 0 }}>
            <label className="cms-label" htmlFor="color-asig">Color</label>
            <input id="color-asig" type="color" value={colorAsig}
              onChange={(e) => setColorAsig(e.target.value)}
              style={{ height: "38px", width: "48px", padding: "2px", border: "1px solid var(--cms-color-border)", borderRadius: "var(--cms-radius-sm)", cursor: "pointer" }} />
          </div>
          <div className="cms-form-group" style={{ marginBottom: 0, alignSelf: "flex-end" }}>
            <label className="cms-label" style={{ display: "inline-flex", alignItems: "center", gap: ".4rem", cursor: "pointer" }}>
              <input type="checkbox" checked={transversalAsig} onChange={(e) => setTransversalAsig(e.target.checked)} />
              Transversal
            </label>
          </div>
          <button type="submit" className="cms-btn cms-btn-primary" style={{ alignSelf: "flex-end" }}>Añadir</button>
        </form>
        <p className="cms-text-muted" style={{ marginTop: ".5rem" }}>
          Una asignatura <strong>transversal</strong> (p. ej. Audición y Lenguaje) no se clasifica por
          ciclo/curso: su contenido aparece en el catálogo dentro de «Aula Abierta».
        </p>
      </section>
    </>
  );
}
