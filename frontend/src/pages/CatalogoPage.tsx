import { useQuery } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../shared/api/client";
import { useConfig } from "../app/config/useConfig";
import type { components } from "../shared/api/schema";

type Contenido = components["schemas"]["ContenidoResponse"];
type Ciclo = components["schemas"]["CicloResponse"];
type Curso = components["schemas"]["CursoResponse"];
type Asignatura = components["schemas"]["AsignaturaResponse"];

// Sentinela para agrupar el contenido de un curso que no tiene asignatura asignada.
const SIN_ASIG = "_sin_";
// Colores alegres para diferenciar los cursos (las asignaturas ya traen su propio color).
const CURSO_COLORS = ["#f59e0b", "#10b981", "#3b82f6", "#ec4899", "#8b5cf6", "#ef4444", "#14b8a6"];

function actividades(n: number): string {
  return n === 1 ? "1 actividad" : `${n} actividades`;
}

function emojiTipo(tipo: string): string {
  return tipo === "interactivo" ? "🎮" : "📖";
}

export function CatalogoPage() {
  const [params, setParams] = useSearchParams();
  const { aula_abierta_label, aula_abierta_emoji } = useConfig();
  const cicloSel = params.get("ciclo");
  const cursoSel = params.get("curso");
  const asigSel = params.get("asignatura");
  const verTodo = params.get("todo") === "1";
  const enAulaAbierta = params.get("transversal") === "1";

  const ciclosQ = useQuery<Ciclo[]>({
    queryKey: ["ciclos"],
    queryFn: () => api.GET("/api/v1/taxonomy/ciclos/").then(({ data }) => data ?? []),
  });
  const cursosQ = useQuery<Curso[]>({
    queryKey: ["cursos"],
    queryFn: () => api.GET("/api/v1/taxonomy/cursos/").then(({ data }) => data ?? []),
  });
  const asigQ = useQuery<Asignatura[]>({
    queryKey: ["asignaturas"],
    queryFn: () => api.GET("/api/v1/taxonomy/asignaturas/").then(({ data }) => data ?? []),
  });
  const contQ = useQuery<Contenido[]>({
    queryKey: ["contenidos-publicos"],
    queryFn: () =>
      api.GET("/api/v1/contenidos/").then(({ data, error }) => {
        if (error) throw new Error("Error al cargar el catálogo");
        return data ?? [];
      }),
  });

  const cargando = ciclosQ.isLoading || cursosQ.isLoading || asigQ.isLoading || contQ.isLoading;
  const error = ciclosQ.isError || cursosQ.isError || asigQ.isError || contQ.isError;

  if (cargando) return <div className="cms-spinner" role="status" aria-label="Cargando" />;
  if (error) return <p className="cms-error">No se pudo cargar el catálogo.</p>;

  const ciclos = ciclosQ.data ?? [];
  const cursos = cursosQ.data ?? [];
  const asignaturas = asigQ.data ?? [];
  const contenidos = contQ.data ?? [];

  // Las asignaturas transversales (p. ej. Audición y Lenguaje) no se clasifican por
  // ciclo/curso: su contenido vive en "Aula Abierta" y se excluye del flujo normal.
  const transversalIds = new Set(asignaturas.filter((a) => a.transversal).map((a) => a.id));
  const esContenidoTransversal = (c: Contenido) =>
    c.asignatura_id != null && transversalIds.has(c.asignatura_id);
  const contenidosNormales = contenidos.filter((c) => !esContenidoTransversal(c));
  const contenidosTransversales = contenidos.filter(esContenidoTransversal);
  const asignaturasTransversales = asignaturas.filter((a) => a.transversal);
  const hayTransversal = contenidosTransversales.length > 0;

  const cicloActual = ciclos.find((c) => c.id === cicloSel) ?? null;
  const curso = cursos.find((c) => c.id === cursoSel) ?? null;
  const asignatura = asignaturas.find((a) => a.id === asigSel) ?? null;
  const colorCurso = (id: string) =>
    CURSO_COLORS[Math.max(0, cursos.findIndex((c) => c.id === id)) % CURSO_COLORS.length];

  // ── Navegación ──────────────────────────────────────────
  const irInicio = () => setParams({});
  const irCurso = (id: string) => setParams({ curso: id });
  const irAsig = (id: string) => setParams({ curso: cursoSel!, asignatura: id });
  const irAulaAbierta = () => setParams({ transversal: "1" });
  const irAulaAsig = (id: string) => setParams({ transversal: "1", asignatura: id });

  // Migas de pan (siempre visibles salvo en la pantalla inicial).
  const crumbs = (
    <nav className="cms-cat-crumbs" aria-label="Dónde estás">
      <button type="button" className="cms-cat-crumb" onClick={irInicio}>🏠 Inicio</button>
      {cicloSel && !curso && cicloActual && (
        <>
          <span className="cms-cat-crumb-sep" aria-hidden>›</span>
          <span className="cms-cat-crumb" aria-current="page">{cicloActual.nombre}</span>
        </>
      )}
      {verTodo && (
        <>
          <span className="cms-cat-crumb-sep" aria-hidden>›</span>
          <span className="cms-cat-crumb" aria-current="page">Todo</span>
        </>
      )}
      {curso && (
        <>
          <span className="cms-cat-crumb-sep" aria-hidden>›</span>
          {asignatura ? (
            <button type="button" className="cms-cat-crumb" onClick={() => irCurso(curso.id)}>
              {curso.nombre}
            </button>
          ) : (
            <span className="cms-cat-crumb" aria-current="page">{curso.nombre}</span>
          )}
        </>
      )}
      {curso && asignatura && (
        <>
          <span className="cms-cat-crumb-sep" aria-hidden>›</span>
          <span className="cms-cat-crumb" aria-current="page">{asignatura.nombre}</span>
        </>
      )}
    </nav>
  );

  // Migas de pan del recorrido Aula Abierta.
  const crumbsAula = (asig: Asignatura | null) => (
    <nav className="cms-cat-crumbs" aria-label="Dónde estás">
      <button type="button" className="cms-cat-crumb" onClick={irInicio}>🏠 Inicio</button>
      <span className="cms-cat-crumb-sep" aria-hidden>›</span>
      {asig ? (
        <button type="button" className="cms-cat-crumb" onClick={irAulaAbierta}>
          {aula_abierta_label}
        </button>
      ) : (
        <span className="cms-cat-crumb" aria-current="page">{aula_abierta_label}</span>
      )}
      {asig && (
        <>
          <span className="cms-cat-crumb-sep" aria-hidden>›</span>
          <span className="cms-cat-crumb" aria-current="page">{asig.nombre}</span>
        </>
      )}
    </nav>
  );

  // ── Tarjetas de contenido (ejercicios / artículos) ──────
  const tarjetaContenido = (c: Contenido) => (
    <Link key={c.id} to={`/contenido/${c.id}`} className="cms-card">
      <span className={`cms-badge cms-badge-${c.tipo}`} style={{ marginBottom: ".5rem" }}>
        {emojiTipo(c.tipo)} {c.tipo}
      </span>
      <p className="cms-h3" style={{ marginTop: ".4rem" }}>{c.titulo}</p>
      {c.descripcion && <p className="cms-muted" style={{ marginTop: ".4rem" }}>{c.descripcion}</p>}
    </Link>
  );

  // Tarjeta de acceso a "Aula Abierta" (asignaturas transversales). Solo si hay contenido.
  const tarjetaAulaAbierta = (
    <button
      type="button"
      className="cms-cat-card"
      style={{ ["--cms-accent" as string]: "#f59e0b" }}
      onClick={irAulaAbierta}
    >
      <span className="cms-cat-emoji">{aula_abierta_emoji}</span>
      <span className="cms-cat-name">{aula_abierta_label}</span>
      <span className="cms-cat-count">{actividades(contenidosTransversales.length)}</span>
    </button>
  );

  const verTodoBtn = (
    <div className="cms-cat-actions">
      <button type="button" className="cms-btn cms-btn-ghost" onClick={() => setParams({ todo: "1" })}>
        Ver todo el catálogo
      </button>
    </div>
  );

  // ── PANTALLA: Aula Abierta — ejercicios de una asignatura transversal ───
  if (enAulaAbierta && asigSel) {
    const items = contenidosTransversales.filter((c) => c.asignatura_id === asigSel);
    const accent = asignatura?.color || "#f59e0b";
    return (
      <>
        {crumbsAula(asignatura)}
        <div className="cms-cat-head">
          <p className="cms-cat-title" style={{ color: accent }}>
            {asignatura ? asignatura.nombre : aula_abierta_label}
          </p>
          <p className="cms-cat-sub">{aula_abierta_label} · {actividades(items.length)}</p>
        </div>
        {items.length === 0 ? (
          <p className="cms-empty">Todavía no hay actividades aquí. ¡Vuelve pronto!</p>
        ) : (
          <div className="cms-grid">{items.map(tarjetaContenido)}</div>
        )}
      </>
    );
  }

  // ── PANTALLA: Aula Abierta — elegir asignatura transversal ─────────────
  if (enAulaAbierta) {
    const conContenido = asignaturasTransversales
      .map((a) => ({ a, n: contenidosTransversales.filter((c) => c.asignatura_id === a.id).length }))
      .filter((x) => x.n > 0);
    return (
      <>
        {crumbsAula(null)}
        <div className="cms-cat-head">
          <p className="cms-cat-title">{aula_abierta_emoji} {aula_abierta_label}</p>
          <p className="cms-cat-sub">Elige una asignatura</p>
        </div>
        {conContenido.length === 0 ? (
          <p className="cms-empty">Todavía no hay actividades aquí. ¡Vuelve pronto!</p>
        ) : (
          <div className="cms-cat-grid">
            {conContenido.map(({ a, n }) => (
              <button
                key={a.id}
                type="button"
                className="cms-cat-card"
                style={{ ["--cms-accent" as string]: a.color || undefined }}
                onClick={() => irAulaAsig(a.id)}
              >
                <span className="cms-cat-letra">{a.nombre.charAt(0).toUpperCase()}</span>
                <span className="cms-cat-name">{a.nombre}</span>
                <span className="cms-cat-count">{actividades(n)}</span>
              </button>
            ))}
          </div>
        )}
      </>
    );
  }

  // ── PANTALLA: Ver todo (lista plana, fallback) ──────────
  if (verTodo) {
    return (
      <>
        {crumbs}
        <h1 className="cms-h1" style={{ marginBottom: "1.5rem" }}>Todo el catálogo</h1>
        {contenidos.length === 0 ? (
          <p className="cms-empty">Aún no hay contenidos publicados.</p>
        ) : (
          <div className="cms-grid">{contenidos.map(tarjetaContenido)}</div>
        )}
      </>
    );
  }

  // ── PANTALLA 3: ejercicios de curso + asignatura ────────
  if (curso && asigSel) {
    const items = contenidosNormales.filter(
      (c) =>
        c.curso_id === curso.id &&
        (asigSel === SIN_ASIG ? c.asignatura_id == null : c.asignatura_id === asigSel),
    );
    const accent = asignatura?.color || colorCurso(curso.id);
    return (
      <>
        {crumbs}
        <div className="cms-cat-head">
          <p className="cms-cat-title" style={{ color: accent }}>
            {asignatura ? asignatura.nombre : "Otras actividades"}
          </p>
          <p className="cms-cat-sub">{curso.nombre} · {actividades(items.length)}</p>
        </div>
        {items.length === 0 ? (
          <p className="cms-empty">Todavía no hay actividades aquí. ¡Vuelve pronto!</p>
        ) : (
          <div className="cms-grid">{items.map(tarjetaContenido)}</div>
        )}
      </>
    );
  }

  // ── PANTALLA 2: elegir asignatura dentro de un curso ────
  if (curso) {
    const delCurso = contenidosNormales.filter((c) => c.curso_id === curso.id);
    const asignaturasConContenido = asignaturas
      .filter((a) => !a.transversal)
      .map((a) => ({ a, n: delCurso.filter((c) => c.asignatura_id === a.id).length }))
      .filter((x) => x.n > 0);
    const sinAsig = delCurso.filter((c) => c.asignatura_id == null).length;

    return (
      <>
        {crumbs}
        <div className="cms-cat-head">
          <p className="cms-cat-title">¿Qué quieres aprender?</p>
          <p className="cms-cat-sub">Elige una asignatura de {curso.nombre}</p>
        </div>
        {asignaturasConContenido.length === 0 && sinAsig === 0 && !hayTransversal ? (
          <p className="cms-empty">Todavía no hay actividades en este curso. ¡Vuelve pronto!</p>
        ) : (
          <div className="cms-cat-grid">
            {asignaturasConContenido.map(({ a, n }) => (
              <button
                key={a.id}
                type="button"
                className="cms-cat-card"
                style={{ ["--cms-accent" as string]: a.color || undefined }}
                onClick={() => irAsig(a.id)}
              >
                <span className="cms-cat-letra">{a.nombre.charAt(0).toUpperCase()}</span>
                <span className="cms-cat-name">{a.nombre}</span>
                <span className="cms-cat-count">{actividades(n)}</span>
              </button>
            ))}
            {sinAsig > 0 && (
              <button
                type="button"
                className="cms-cat-card"
                onClick={() => irAsig(SIN_ASIG)}
              >
                <span className="cms-cat-emoji">✨</span>
                <span className="cms-cat-name">Otras actividades</span>
                <span className="cms-cat-count">{actividades(sinAsig)}</span>
              </button>
            )}
            {hayTransversal && tarjetaAulaAbierta}
          </div>
        )}
      </>
    );
  }

  // ── PANTALLA 1: elegir curso (inicio) ───────────────────
  const cursosConContenido = new Set(contenidosNormales.map((c) => c.curso_id).filter(Boolean));
  const ciclosConCursos = ciclos
    .map((ci) => ({
      ciclo: ci,
      cursos: cursos.filter((cu) => cu.ciclo_id === ci.id && cursosConContenido.has(cu.id)),
    }))
    .filter((g) => g.cursos.length > 0);
  // Si venimos de un enlace de ciclo (?ciclo=), mostrar solo ese ciclo.
  const ciclosVisibles = cicloSel
    ? ciclosConCursos.filter((g) => g.ciclo.id === cicloSel)
    : ciclosConCursos;
  const hayContenido = contenidos.length > 0;

  return (
    <>
      {cicloSel && crumbs}
      <div className="cms-cat-head">
        <p className="cms-cat-title">¿En qué curso estás?</p>
        <p className="cms-cat-sub">
          {cicloActual ? `Cursos de ${cicloActual.nombre}` : "Toca tu curso para ver las actividades"}
        </p>
      </div>

      {!hayContenido ? (
        <p className="cms-empty">Aún no hay contenidos publicados.</p>
      ) : (
        <>
          {ciclosVisibles.map(({ ciclo, cursos: cs }) => (
            <section key={ciclo.id} className="cms-cat-section">
              <p className="cms-cat-section-title">{ciclo.nombre}</p>
              <div className="cms-cat-grid">
                {cs.map((cu) => {
                  const n = contenidosNormales.filter((c) => c.curso_id === cu.id).length;
                  return (
                    <button
                      key={cu.id}
                      type="button"
                      className="cms-cat-card"
                      style={{ ["--cms-accent" as string]: colorCurso(cu.id) }}
                      onClick={() => irCurso(cu.id)}
                    >
                      <span className="cms-cat-emoji">🎒</span>
                      <span className="cms-cat-name">{cu.nombre}</span>
                      <span className="cms-cat-count">{actividades(n)}</span>
                    </button>
                  );
                })}
              </div>
            </section>
          ))}

          {/* Acceso a las asignaturas transversales (independiente de ciclo/curso). */}
          {hayTransversal && (
            <section className="cms-cat-section">
              <p className="cms-cat-section-title">Apoyo y diversidad</p>
              <div className="cms-cat-grid">{tarjetaAulaAbierta}</div>
            </section>
          )}

          {ciclosVisibles.length === 0 && !hayTransversal && (
            <p className="cms-empty">Las actividades todavía no están organizadas por curso.</p>
          )}
          {verTodoBtn}
        </>
      )}
    </>
  );
}
