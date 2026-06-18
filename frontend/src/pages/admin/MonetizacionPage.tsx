import { FormEvent, useEffect, useState } from "react";
import { useConfig, useConfigMutations } from "../../app/config/useConfig";
import type { components } from "../../shared/api/schema";
import { REDES_SOCIALES, IconoRed } from "../../app/config/redesSociales";

type AjustesGeneralesPayload = components["schemas"]["AjustesGeneralesRequest"];
type Donacion = components["schemas"]["DonacionResponse"];
type RedSocial = components["schemas"]["RedSocialResponse"];

// Formulario de Monetización y RRSS: enlaces de donación, redes sociales y publicidad.
// Parte de `base` (la config actual completa) y solo sobrescribe estas tres secciones, de modo
// que guardar aquí NO altera los ajustes de Apariencia (el PUT /config/general reemplaza todo).
function MonetizacionForm({
  base,
  donacionesInicial,
  redesInicial,
  publiActivaInicial,
  publiIzqInicial,
  publiDerInicial,
  onGuardar,
}: {
  base: AjustesGeneralesPayload;
  donacionesInicial: Donacion[];
  redesInicial: RedSocial[];
  publiActivaInicial: boolean;
  publiIzqInicial: string;
  publiDerInicial: string;
  onGuardar: (ajustes: AjustesGeneralesPayload) => Promise<void>;
}) {
  const [donaciones, setDonaciones] = useState<Donacion[]>(donacionesInicial);
  const [redes, setRedes] = useState<RedSocial[]>(redesInicial);
  const [publiActiva, setPubliActiva] = useState(publiActivaInicial);
  const [publiIzq, setPubliIzq] = useState(publiIzqInicial);
  const [publiDer, setPubliDer] = useState(publiDerInicial);
  const [guardando, setGuardando] = useState(false);
  const [guardado, setGuardado] = useState(false);

  useEffect(() => setDonaciones(donacionesInicial), [donacionesInicial]);
  useEffect(() => setRedes(redesInicial), [redesInicial]);
  useEffect(() => setPubliActiva(publiActivaInicial), [publiActivaInicial]);
  useEffect(() => setPubliIzq(publiIzqInicial), [publiIzqInicial]);
  useEffect(() => setPubliDer(publiDerInicial), [publiDerInicial]);

  const tocado = () => setGuardado(false);

  function actualizarDonacion(i: number, campo: keyof Donacion, valor: string) {
    setDonaciones((prev) => prev.map((d, j) => (j === i ? { ...d, [campo]: valor } : d)));
    tocado();
  }
  function anadirDonacion() {
    setDonaciones((prev) => [...prev, { etiqueta: "", url: "" }]);
    tocado();
  }
  function quitarDonacion(i: number) {
    setDonaciones((prev) => prev.filter((_, j) => j !== i));
    tocado();
  }

  function actualizarRed(i: number, campo: keyof RedSocial, valor: string) {
    setRedes((prev) => prev.map((r, j) => (j === i ? { ...r, [campo]: valor } : r)));
    tocado();
  }
  function anadirRed() {
    setRedes((prev) => [...prev, { red: REDES_SOCIALES[0].id, url: "" }]);
    tocado();
  }
  function quitarRed(i: number) {
    setRedes((prev) => prev.filter((_, j) => j !== i));
    tocado();
  }

  const sucio =
    JSON.stringify(donaciones) !== JSON.stringify(donacionesInicial) ||
    JSON.stringify(redes) !== JSON.stringify(redesInicial) ||
    publiActiva !== publiActivaInicial ||
    publiIzq !== publiIzqInicial ||
    publiDer !== publiDerInicial;

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (guardando) return;
    setGuardando(true);
    setGuardado(false);
    onGuardar({
      ...base,
      // Descarta filas de donación incompletas (sin etiqueta o sin URL).
      donaciones: donaciones
        .map((d) => ({ etiqueta: d.etiqueta.trim(), url: d.url.trim() }))
        .filter((d) => d.etiqueta && d.url),
      // Descarta redes sin URL.
      redes_sociales: redes
        .map((r) => ({ red: r.red, url: r.url.trim() }))
        .filter((r) => r.url),
      publicidad_activa: publiActiva,
      publicidad_html_izquierda: publiIzq,
      publicidad_html_derecha: publiDer,
    })
      .then(() => setGuardado(true))
      .catch(() => setGuardado(false)) // el error se muestra a nivel de página
      .finally(() => setGuardando(false));
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2 className="cms-h2" style={{ marginBottom: ".4rem" }}>Enlaces de donación</h2>
      <p className="cms-text-muted" style={{ marginBottom: ".6rem" }}>
        Botones de donación que aparecen en el pie de la web pública (PayPal, Ko-fi, etc.). La URL debe
        empezar por https://
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: ".5rem", marginBottom: ".75rem" }}>
        {donaciones.map((d, i) => (
          <div key={i} style={{ display: "flex", gap: ".5rem", flexWrap: "wrap", alignItems: "center" }}>
            <input
              className="cms-input"
              style={{ width: 150 }}
              value={d.etiqueta}
              maxLength={40}
              onChange={(e) => actualizarDonacion(i, "etiqueta", e.target.value)}
              placeholder="PayPal"
              aria-label={`Etiqueta del enlace ${i + 1}`}
            />
            <input
              className="cms-input"
              style={{ flex: 1, minWidth: 220 }}
              value={d.url}
              maxLength={500}
              onChange={(e) => actualizarDonacion(i, "url", e.target.value)}
              placeholder="https://paypal.me/tucuenta"
              aria-label={`URL del enlace ${i + 1}`}
            />
            <button type="button" className="cms-btn cms-btn-ghost" onClick={() => quitarDonacion(i)}>
              Quitar
            </button>
          </div>
        ))}
      </div>
      <button
        type="button"
        className="cms-btn cms-btn-ghost"
        style={{ marginBottom: "2rem" }}
        onClick={anadirDonacion}
      >
        + Añadir enlace de donación
      </button>

      <h2 className="cms-h2" style={{ marginBottom: ".4rem" }}>Redes sociales</h2>
      <p className="cms-text-muted" style={{ marginBottom: ".6rem" }}>
        Iconos enlazados a tus perfiles, mostrados en el pie de la web pública. La URL debe empezar
        por https://
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: ".5rem", marginBottom: ".75rem" }}>
        {redes.map((r, i) => (
          <div key={i} style={{ display: "flex", gap: ".5rem", flexWrap: "wrap", alignItems: "center" }}>
            <IconoRed id={r.red} size={24} />
            <select
              className="cms-select"
              style={{ width: 150 }}
              value={r.red}
              onChange={(e) => actualizarRed(i, "red", e.target.value)}
              aria-label={`Red social ${i + 1}`}
            >
              {REDES_SOCIALES.map((rs) => (
                <option key={rs.id} value={rs.id}>{rs.label}</option>
              ))}
            </select>
            <input
              className="cms-input"
              style={{ flex: 1, minWidth: 220 }}
              value={r.url}
              maxLength={500}
              onChange={(e) => actualizarRed(i, "url", e.target.value)}
              placeholder="https://…"
              aria-label={`URL de la red ${i + 1}`}
            />
            <button type="button" className="cms-btn cms-btn-ghost" onClick={() => quitarRed(i)}>
              Quitar
            </button>
          </div>
        ))}
      </div>
      <button
        type="button"
        className="cms-btn cms-btn-ghost"
        style={{ marginBottom: "2rem" }}
        onClick={anadirRed}
      >
        + Añadir red social
      </button>

      <h2 className="cms-h2" style={{ marginBottom: ".4rem" }}>Publicidad en los márgenes</h2>
      <p className="cms-text-muted" style={{ marginBottom: ".6rem" }}>
        Anuncios en los márgenes izquierdo y derecho, <strong>solo en las pantallas de navegación</strong>
        {" "}del catálogo. Nunca se muestran durante un ejercicio (lo usa un menor) ni en el panel. Pega
        aquí el código HTML de tu red de anuncios.
      </p>
      <label
        style={{ display: "flex", alignItems: "center", gap: ".5rem", marginBottom: ".75rem", cursor: "pointer" }}
      >
        <input
          type="checkbox"
          checked={publiActiva}
          onChange={(e) => { setPubliActiva(e.target.checked); tocado(); }}
        />
        <span>Mostrar publicidad en las pantallas de navegación</span>
      </label>
      <div style={{ display: "flex", gap: ".75rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
        <div className="cms-form-group" style={{ marginBottom: 0, flex: 1, minWidth: 260 }}>
          <label className="cms-label" htmlFor="cms-publi-izq">Código del margen izquierdo</label>
          <textarea
            id="cms-publi-izq"
            className="cms-textarea"
            rows={4}
            value={publiIzq}
            maxLength={8000}
            onChange={(e) => { setPubliIzq(e.target.value); tocado(); }}
            placeholder="<script>…</script> o <ins>…</ins>"
          />
        </div>
        <div className="cms-form-group" style={{ marginBottom: 0, flex: 1, minWidth: 260 }}>
          <label className="cms-label" htmlFor="cms-publi-der">Código del margen derecho</label>
          <textarea
            id="cms-publi-der"
            className="cms-textarea"
            rows={4}
            value={publiDer}
            maxLength={8000}
            onChange={(e) => { setPubliDer(e.target.value); tocado(); }}
            placeholder="<script>…</script> o <ins>…</ins>"
          />
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: ".75rem" }}>
        <button type="submit" className="cms-btn cms-btn-primary" disabled={!sucio || guardando}>
          {guardando ? "Guardando…" : "Guardar cambios"}
        </button>
        {guardado && !sucio && (
          <span style={{ color: "var(--cms-color-success)", fontSize: ".85rem" }} role="status">
            ✓ Guardado
          </span>
        )}
      </div>
    </form>
  );
}

export function MonetizacionPage() {
  const {
    ajustesActuales,
    donaciones,
    redes_sociales,
    publicidad_activa,
    publicidad_html_izquierda,
    publicidad_html_derecha,
    isLoading,
  } = useConfig();
  const { guardarAjustesGenerales } = useConfigMutations();
  const [error, setError] = useState<string | null>(null);

  if (isLoading) return <div className="cms-spinner" role="status" aria-label="Cargando" />;

  return (
    <>
      <div className="cms-admin-header">
        <h1 className="cms-h1">Monetización y RRSS</h1>
      </div>

      <p className="cms-text-muted" style={{ marginBottom: "1.5rem" }}>
        Donaciones, redes sociales y publicidad. Todo se muestra en la <strong>zona pública</strong>;
        la publicidad solo en las pantallas de navegación (nunca durante un ejercicio).
      </p>

      {error && (
        <div role="alert" className="cms-alert-error" style={{ marginBottom: "1.5rem" }}>
          {error}
        </div>
      )}

      <MonetizacionForm
        base={ajustesActuales}
        donacionesInicial={donaciones}
        redesInicial={redes_sociales}
        publiActivaInicial={publicidad_activa}
        publiIzqInicial={publicidad_html_izquierda}
        publiDerInicial={publicidad_html_derecha}
        onGuardar={(ajustes) => {
          setError(null);
          return guardarAjustesGenerales(ajustes).catch((e: unknown) => {
            setError(e instanceof Error ? e.message : "Error inesperado.");
            throw e;
          });
        }}
      />
    </>
  );
}
