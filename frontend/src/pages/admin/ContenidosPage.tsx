import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../shared/api/client";
import type { components } from "../../shared/api/schema";

type Contenido = components["schemas"]["ContenidoResponse"];
type Ciclo = components["schemas"]["CicloResponse"];
type Curso = components["schemas"]["CursoResponse"];
type Asignatura = components["schemas"]["AsignaturaResponse"];

const POR_PAGINA = 10;

type ClaveOrden = "titulo" | "tipo" | "ciclo" | "curso" | "asignatura" | "estado" | "visitas";

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

  // Visitas por contenido (mapa id -> nº). Si falla, se muestran 0 (no bloquea la lista).
  const { data: visitas } = useQuery({
    queryKey: ["admin-visitas"],
    queryFn: () =>
      api.GET("/api/v1/analytics/visitas").then(({ data }) => data?.por_contenido ?? {}),
  });

  // Taxonomía para mostrar los nombres de ciclo/curso/asignatura (el contenido solo trae IDs).
  // Comparten queryKey con el catálogo, así que se sirven de la caché de React Query.
  const { data: ciclos } = useQuery<Ciclo[]>({
    queryKey: ["ciclos"],
    queryFn: () => api.GET("/api/v1/taxonomy/ciclos/").then(({ data }) => data ?? []),
  });
  const { data: cursos } = useQuery<Curso[]>({
    queryKey: ["cursos"],
    queryFn: () => api.GET("/api/v1/taxonomy/cursos/").then(({ data }) => data ?? []),
  });
  const { data: asignaturas } = useQuery<Asignatura[]>({
    queryKey: ["asignaturas"],
    queryFn: () => api.GET("/api/v1/taxonomy/asignaturas/").then(({ data }) => data ?? []),
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

  const purgar = useMutation({
    mutationFn: (id: string) =>
      api.DELETE("/api/v1/contenidos/{contenido_id}/purgar", {
        params: { path: { contenido_id: id } },
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-contenidos"] }),
  });

  const [confirmar, setConfirmar] = useState<string | null>(null);
  const [confirmarPurga, setConfirmarPurga] = useState<string | null>(null);
  const [orden, setOrden] = useState<{ clave: ClaveOrden; asc: boolean }>({
    clave: "titulo",
    asc: true,
  });
  const [pagina, setPagina] = useState(1);

  // Mapas id -> nombre para resolver la taxonomía de cada contenido.
  const nombreCiclo = useMemo(
    () => new Map((ciclos ?? []).map((x) => [x.id, x.nombre])),
    [ciclos],
  );
  const nombreCurso = useMemo(
    () => new Map((cursos ?? []).map((x) => [x.id, x.nombre])),
    [cursos],
  );
  const nombreAsignatura = useMemo(
    () => new Map((asignaturas ?? []).map((x) => [x.id, x.nombre])),
    [asignaturas],
  );

  const cicloDe = (c: Contenido) => (c.ciclo_id ? nombreCiclo.get(c.ciclo_id) ?? "" : "");
  const cursoDe = (c: Contenido) => (c.curso_id ? nombreCurso.get(c.curso_id) ?? "" : "");
  const asignaturaDe = (c: Contenido) =>
    c.asignatura_id ? nombreAsignatura.get(c.asignatura_id) ?? "" : "";

  // Lista ordenada según la columna activa. Las cadenas comparan con locale español; las
  // visitas, numéricamente. La taxonomía sin asignar (cadena vacía) cae al final en ascendente.
  const ordenados = useMemo(() => {
    const filas = [...(data ?? [])];
    const { clave, asc } = orden;
    const valor = (c: Contenido): string | number => {
      switch (clave) {
        case "titulo": return c.titulo;
        case "tipo": return c.tipo;
        case "ciclo": return cicloDe(c);
        case "curso": return cursoDe(c);
        case "asignatura": return asignaturaDe(c);
        case "estado": return estadoLabel(c);
        case "visitas": return visitas?.[c.id] ?? 0;
      }
    };
    filas.sort((a, b) => {
      const va = valor(a);
      const vb = valor(b);
      let cmp: number;
      if (typeof va === "number" && typeof vb === "number") {
        cmp = va - vb;
      } else {
        const sa = String(va);
        const sb = String(vb);
        // Las cadenas vacías (sin asignar) van siempre al final, sea cual sea el sentido.
        if (sa === "" && sb !== "") return 1;
        if (sb === "" && sa !== "") return -1;
        cmp = sa.localeCompare(sb, "es", { sensitivity: "base" });
      }
      return asc ? cmp : -cmp;
    });
    return filas;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, orden, visitas, nombreCiclo, nombreCurso, nombreAsignatura]);

  const totalPaginas = Math.max(1, Math.ceil(ordenados.length / POR_PAGINA));
  const paginaActual = Math.min(pagina, totalPaginas);
  const visibles = ordenados.slice(
    (paginaActual - 1) * POR_PAGINA,
    paginaActual * POR_PAGINA,
  );

  function ordenarPor(clave: ClaveOrden) {
    setOrden((prev) =>
      prev.clave === clave ? { clave, asc: !prev.asc } : { clave, asc: true },
    );
    setPagina(1);
  }

  function flecha(clave: ClaveOrden) {
    if (orden.clave !== clave) return null;
    return <span className="cms-sort-arrow">{orden.asc ? "▲" : "▼"}</span>;
  }

  if (isLoading) return <div className="cms-spinner" role="status" aria-label="Cargando" />;
  if (isError) return <p className="cms-error">No se pudo cargar la lista de contenidos.</p>;

  const cabecera = (clave: ClaveOrden, texto: string) => (
    <th
      className="cms-th-sortable"
      aria-sort={orden.clave === clave ? (orden.asc ? "ascending" : "descending") : "none"}
      onClick={() => ordenarPor(clave)}
    >
      {texto}
      {flecha(clave)}
    </th>
  );

  return (
    <>
      <div className="cms-admin-header">
        <h1 className="cms-h1">Contenidos</h1>
        <div style={{ display: "flex", gap: ".5rem", flexWrap: "wrap" }}>
          <Link to="/admin/contenidos/nuevo?tipo=texto" className="cms-btn cms-btn-ghost">
            + Artículo de texto
          </Link>
          <Link to="/admin/contenidos/nuevo?tipo=pdf" className="cms-btn cms-btn-ghost">
            + Ficha PDF
          </Link>
          <Link to="/admin/contenidos/nuevo?tipo=interactivo" className="cms-btn cms-btn-primary">
            + Ejercicio interactivo
          </Link>
        </div>
      </div>
      {!data?.length ? (
        <p className="cms-empty">No hay contenidos creados todavía.</p>
      ) : (
        <>
          <table className="cms-table">
            <thead>
              <tr>
                {cabecera("titulo", "Título")}
                {cabecera("tipo", "Tipo")}
                {cabecera("ciclo", "Ciclo")}
                {cabecera("curso", "Curso")}
                {cabecera("asignatura", "Asignatura")}
                {cabecera("estado", "Estado")}
                {cabecera("visitas", "Visitas")}
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {visibles.map((c) => (
                <tr key={c.id}>
                  <td>{c.titulo}</td>
                  <td>
                    <span className={`cms-badge cms-badge-${c.tipo}`}>{c.tipo}</span>
                  </td>
                  <td>{cicloDe(c) || <span className="cms-text-muted">—</span>}</td>
                  <td>{cursoDe(c) || <span className="cms-text-muted">—</span>}</td>
                  <td>{asignaturaDe(c) || <span className="cms-text-muted">—</span>}</td>
                  <td>
                    <span className={`cms-badge cms-badge-${badgeClass(c)}`}>
                      {estadoLabel(c)}
                    </span>
                  </td>
                  <td>{visitas?.[c.id] ?? 0}</td>
                  <td style={{ display: "flex", gap: ".4rem", flexWrap: "wrap" }}>
                    {!c.borrado && (
                      <Link
                        to={`/admin/contenidos/${c.id}/editar`}
                        className="cms-btn cms-btn-ghost"
                      >
                        Editar
                      </Link>
                    )}
                    {!c.publicado && !c.borrado && (
                      <button
                        className="cms-btn cms-btn-primary"
                        onClick={() => publicar.mutate(c.id)}
                      >
                        Publicar
                      </button>
                    )}
                    {c.borrado ? (
                      confirmarPurga === c.id ? (
                        <>
                          <button
                            className="cms-btn cms-btn-danger"
                            onClick={() => { purgar.mutate(c.id); setConfirmarPurga(null); }}
                          >
                            Confirmar eliminación
                          </button>
                          <button
                            className="cms-btn cms-btn-ghost"
                            onClick={() => setConfirmarPurga(null)}
                          >
                            Cancelar
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            className="cms-btn cms-btn-ghost"
                            onClick={() => restaurar.mutate(c.id)}
                          >
                            Restaurar
                          </button>
                          <button
                            className="cms-btn cms-btn-danger"
                            onClick={() => setConfirmarPurga(c.id)}
                          >
                            Eliminar definitivamente
                          </button>
                        </>
                      )
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
          {totalPaginas > 1 && (
            <nav className="cms-pagination" aria-label="Paginación de contenidos">
              <button
                className="cms-btn cms-btn-ghost"
                onClick={() => setPagina(1)}
                disabled={paginaActual === 1}
                aria-label="Primera página"
              >
                « Primero
              </button>
              <button
                className="cms-btn cms-btn-ghost"
                onClick={() => setPagina((p) => Math.max(1, p - 1))}
                disabled={paginaActual === 1}
                aria-label="Página anterior"
              >
                ‹ Anterior
              </button>
              <span className="cms-pagination-info">
                Página {paginaActual} de {totalPaginas}
              </span>
              <button
                className="cms-btn cms-btn-ghost"
                onClick={() => setPagina((p) => Math.min(totalPaginas, p + 1))}
                disabled={paginaActual === totalPaginas}
                aria-label="Página siguiente"
              >
                Siguiente ›
              </button>
              <button
                className="cms-btn cms-btn-ghost"
                onClick={() => setPagina(totalPaginas)}
                disabled={paginaActual === totalPaginas}
                aria-label="Última página"
              >
                Último »
              </button>
            </nav>
          )}
        </>
      )}
    </>
  );
}
