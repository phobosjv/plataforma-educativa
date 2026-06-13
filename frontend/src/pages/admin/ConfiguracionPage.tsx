import { FormEvent, useEffect, useState } from "react";
import { useConfig, useConfigMutations } from "../../app/config/useConfig";
import { PALETAS_PREDEFINIDAS, type Palette } from "../../app/config/palettes";
import { FUENTES } from "../../app/config/fonts";
import { FONDOS, urlPatron } from "../../app/config/backgrounds";

// ── Ajustes generales: nombre del sitio + fuente + fondo ──────────────────────

function AjustesGenerales({
  nombreInicial,
  fuenteInicial,
  fondoInicial,
  onGuardar,
}: {
  nombreInicial: string;
  fuenteInicial: string;
  fondoInicial: string;
  onGuardar: (nombre: string, fuente: string, fondo: string) => Promise<void>;
}) {
  const [nombre, setNombre] = useState(nombreInicial);
  const [fuente, setFuente] = useState(fuenteInicial);
  const [fondo, setFondo] = useState(fondoInicial);
  const [guardando, setGuardando] = useState(false);
  const [guardado, setGuardado] = useState(false);

  // Sincroniza si la config llega/actualiza desde el servidor.
  useEffect(() => setNombre(nombreInicial), [nombreInicial]);
  useEffect(() => setFuente(fuenteInicial), [fuenteInicial]);
  useEffect(() => setFondo(fondoInicial), [fondoInicial]);

  const sucio =
    nombre.trim() !== nombreInicial || fuente !== fuenteInicial || fondo !== fondoInicial;

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!nombre.trim() || guardando) return;
    setGuardando(true);
    setGuardado(false);
    onGuardar(nombre.trim(), fuente, fondo)
      .then(() => setGuardado(true))
      .catch(() => setGuardado(false)) // el error se muestra a nivel de página
      .finally(() => setGuardando(false));
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "2.5rem" }}>
      <div className="cms-form-group" style={{ maxWidth: 420 }}>
        <label className="cms-label" htmlFor="cms-nombre-sitio">Nombre del sitio</label>
        <input
          id="cms-nombre-sitio"
          className="cms-input"
          value={nombre}
          maxLength={80}
          onChange={(e) => { setNombre(e.target.value); setGuardado(false); }}
          placeholder="Plataforma Educativa"
          required
        />
      </div>

      <label className="cms-label" style={{ display: "block", marginBottom: ".6rem" }}>
        Fuente de letra
      </label>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: ".75rem",
          marginBottom: "1.25rem",
        }}
      >
        {FUENTES.map((f) => {
          const activa = fuente === f.id;
          return (
            <button
              type="button"
              key={f.id}
              onClick={() => { setFuente(f.id); setGuardado(false); }}
              aria-pressed={activa}
              style={{
                textAlign: "left",
                cursor: "pointer",
                background: "var(--cms-color-surface)",
                border: activa
                  ? "2px solid var(--cms-color-primary)"
                  : "1px solid var(--cms-color-border)",
                borderRadius: "var(--cms-radius)",
                padding: ".75rem .9rem",
                boxShadow: activa ? "0 0 0 2px var(--cms-color-primary)" : "none",
              }}
            >
              <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 6 }}>
                <span style={{ fontFamily: f.stack, fontSize: "1.25rem", fontWeight: 700, color: "var(--cms-color-fg)" }}>
                  {f.nombre}
                </span>
                <span className="cms-badge" style={{ background: "var(--cms-color-bg)", color: "var(--cms-color-muted)" }}>
                  {f.categoria}
                </span>
              </div>
              {/* Muestra del alfabeto en la propia fuente */}
              <div style={{ fontFamily: f.stack, fontSize: "1rem", color: "var(--cms-color-fg)", marginTop: 4 }}>
                Hola, ¡a leer! AaBbCc 123
              </div>
              <div className="cms-muted" style={{ marginTop: 4 }}>{f.descripcion}</div>
            </button>
          );
        })}
      </div>

      <label className="cms-label" style={{ display: "block", marginBottom: ".6rem" }}>
        Fondo del sitio (estampado)
      </label>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))",
          gap: ".75rem",
          marginBottom: "1.25rem",
        }}
      >
        {FONDOS.map((f) => {
          const activo = fondo === f.id;
          const patron = urlPatron(f.id);
          return (
            <button
              type="button"
              key={f.id}
              onClick={() => { setFondo(f.id); setGuardado(false); }}
              aria-pressed={activo}
              title={f.descripcion}
              style={{
                textAlign: "left",
                cursor: "pointer",
                background: "var(--cms-color-surface)",
                border: activo
                  ? "2px solid var(--cms-color-primary)"
                  : "1px solid var(--cms-color-border)",
                borderRadius: "var(--cms-radius)",
                padding: ".5rem",
                boxShadow: activo ? "0 0 0 2px var(--cms-color-primary)" : "none",
              }}
            >
              {/* Preview del estampado recoloreado con la paleta (misma técnica de máscara) */}
              <div
                style={{
                  height: 64,
                  borderRadius: "var(--cms-radius-sm)",
                  background: patron ? "var(--cms-color-bg)" : "var(--cms-color-bg)",
                  position: "relative",
                  overflow: "hidden",
                  border: "1px solid var(--cms-color-border)",
                }}
              >
                {patron ? (
                  <span
                    aria-hidden
                    style={{
                      position: "absolute",
                      inset: 0,
                      backgroundColor: "var(--cms-color-primary)",
                      opacity: 0.55,
                      WebkitMaskImage: `url("${patron}")`,
                      maskImage: `url("${patron}")`,
                      WebkitMaskRepeat: "repeat",
                      maskRepeat: "repeat",
                      WebkitMaskSize: "120px 120px",
                      maskSize: "120px 120px",
                    }}
                  />
                ) : (
                  <span
                    style={{
                      position: "absolute",
                      inset: 0,
                      display: "grid",
                      placeItems: "center",
                      color: "var(--cms-color-muted)",
                      fontSize: ".8rem",
                    }}
                  >
                    sin estampado
                  </span>
                )}
              </div>
              <div style={{ fontWeight: 600, marginTop: ".4rem", fontSize: ".9rem" }}>{f.nombre}</div>
            </button>
          );
        })}
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

// ── Swatch de paleta ──────────────────────────────────────────────────────────

function PaletaSwatch({
  paleta,
  activa,
  onSelect,
  onDelete,
}: {
  paleta: Palette;
  activa: boolean;
  onSelect: () => void;
  onDelete?: () => void;
}) {
  return (
    <div
      style={{
        border: activa ? "3px solid var(--cms-color-primary)" : "3px solid transparent",
        borderRadius: "var(--cms-radius)",
        overflow: "hidden",
        cursor: "pointer",
        boxShadow: activa ? "0 0 0 2px var(--cms-color-primary)" : "var(--cms-shadow)",
        transition: "all .15s",
        position: "relative",
      }}
      onClick={onSelect}
      role="button"
      aria-pressed={activa}
      title={`Activar "${paleta.nombre}"`}
    >
      {/* Preview */}
      <div style={{ background: paleta.colores.bg, padding: "12px 14px" }}>
        <div
          style={{
            background: paleta.colores.surface,
            borderRadius: 6,
            padding: "8px 10px",
            boxShadow: "0 1px 3px rgba(0,0,0,.1)",
          }}
        >
          <div
            style={{
              width: "60%",
              height: 8,
              borderRadius: 4,
              background: paleta.colores.primary,
              marginBottom: 6,
            }}
          />
          <div
            style={{
              width: "90%",
              height: 6,
              borderRadius: 4,
              background: paleta.colores.fg,
              opacity: 0.3,
            }}
          />
          <div
            style={{
              width: "75%",
              height: 6,
              borderRadius: 4,
              background: paleta.colores.fg,
              opacity: 0.2,
              marginTop: 4,
            }}
          />
        </div>
      </div>

      {/* Label */}
      <div
        style={{
          padding: "8px 12px",
          background: paleta.colores.surface,
          borderTop: `1px solid ${paleta.colores.fg}1a`,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 6,
        }}
      >
        <span style={{ fontSize: ".82rem", fontWeight: 600, color: paleta.colores.fg }}>
          {paleta.emoji} {paleta.nombre}
        </span>
        {onDelete && (
          <button
            onClick={(e) => { e.stopPropagation(); onDelete(); }}
            style={{
              background: "none", border: "none", cursor: "pointer",
              color: "#dc2626", fontSize: ".75rem", padding: "2px 4px",
            }}
            title="Eliminar paleta"
          >
            ✕
          </button>
        )}
      </div>

      {activa && (
        <div
          style={{
            position: "absolute", top: 8, right: 8,
            background: paleta.colores.primary, color: "#fff",
            borderRadius: 999, fontSize: ".7rem", fontWeight: 700,
            padding: "2px 8px",
          }}
        >
          Activa
        </div>
      )}
    </div>
  );
}

// ── Formulario nueva paleta personalizada ─────────────────────────────────────

function FormNuevaPaleta({ onGuardar }: { onGuardar: (p: Omit<Palette, "predefinida" | "emoji">) => void }) {
  const [abierto, setAbierto] = useState(false);
  const [nombre, setNombre] = useState("");
  const [colores, setColores] = useState({
    bg: "#f8fafc",
    surface: "#ffffff",
    fg: "#1f2937",
    primary: "#4f46e5",
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!nombre.trim()) return;
    onGuardar({
      id: crypto.randomUUID(),
      nombre: nombre.trim(),
      colores,
    });
    setNombre("");
    setAbierto(false);
  }

  if (!abierto) {
    return (
      <button
        className="cms-btn cms-btn-ghost"
        style={{ height: "100%", minHeight: 110, width: "100%", fontSize: "1.5rem", flexDirection: "column", gap: ".4rem" }}
        onClick={() => setAbierto(true)}
      >
        <span>+</span>
        <span style={{ fontSize: ".8rem" }}>Nueva paleta</span>
      </button>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        background: "var(--cms-color-surface)",
        border: "1px solid var(--cms-color-border)",
        borderRadius: "var(--cms-radius)",
        padding: "1rem",
      }}
    >
      <div className="cms-form-group">
        <label className="cms-label">Nombre</label>
        <input
          className="cms-input"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          placeholder="Mi paleta"
          required
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: ".75rem", marginBottom: "1rem" }}>
        {(["bg", "surface", "fg", "primary"] as const).map((key) => (
          <div key={key} className="cms-form-group" style={{ marginBottom: 0 }}>
            <label className="cms-label" style={{ display: "flex", alignItems: "center", gap: ".4rem" }}>
              <input
                type="color"
                value={colores[key]}
                onChange={(e) => setColores({ ...colores, [key]: e.target.value })}
                style={{ width: 28, height: 28, padding: 1, border: "1px solid var(--cms-color-border)", borderRadius: 4, cursor: "pointer" }}
              />
              {{ bg: "Fondo", surface: "Superficie", fg: "Texto", primary: "Color principal" }[key]}
            </label>
          </div>
        ))}
      </div>

      {/* Preview en vivo */}
      <div
        style={{
          background: colores.bg, borderRadius: 6, padding: "10px 12px", marginBottom: "1rem",
          border: "1px solid rgba(0,0,0,.08)",
        }}
      >
        <div style={{ background: colores.surface, borderRadius: 4, padding: "8px 10px", boxShadow: "0 1px 3px rgba(0,0,0,.1)" }}>
          <div style={{ width: "55%", height: 8, borderRadius: 4, background: colores.primary, marginBottom: 5 }} />
          <div style={{ width: "85%", height: 5, borderRadius: 4, background: colores.fg, opacity: 0.3 }} />
        </div>
      </div>

      <div style={{ display: "flex", gap: ".5rem" }}>
        <button type="submit" className="cms-btn cms-btn-primary">Guardar</button>
        <button type="button" className="cms-btn cms-btn-ghost" onClick={() => setAbierto(false)}>Cancelar</button>
      </div>
    </form>
  );
}

// ── Página principal ──────────────────────────────────────────────────────────

export function ConfiguracionPage() {
  const { nombre_sitio, fuente_activa, fondo_activo, paleta_activa, personalizadas, isLoading } =
    useConfig();
  const { guardarAjustesGenerales, activarPaleta, agregarPaleta, eliminarPaleta } =
    useConfigMutations();
  const [error, setError] = useState<string | null>(null);

  // Envuelve una mutación: limpia el error previo y captura cualquier fallo
  // para mostrarlo en pantalla en vez de tragárselo en silencio.
  function ejecutar(accion: () => Promise<void>) {
    setError(null);
    accion().catch((e: unknown) =>
      setError(e instanceof Error ? e.message : "Error inesperado."),
    );
  }

  if (isLoading) return <div className="cms-spinner" role="status" aria-label="Cargando" />;

  return (
    <>
      <div className="cms-admin-header">
        <h1 className="cms-h1">Apariencia y ajustes</h1>
      </div>

      {error && (
        <div
          role="alert"
          style={{
            background: "#fef2f2",
            border: "1px solid #fecaca",
            color: "#b91c1c",
            borderRadius: "var(--cms-radius)",
            padding: ".75rem 1rem",
            marginBottom: "1.5rem",
            fontSize: ".9rem",
          }}
        >
          {error}
        </div>
      )}

      <h2 className="cms-h2" style={{ marginBottom: "1rem" }}>Ajustes generales</h2>
      <AjustesGenerales
        nombreInicial={nombre_sitio}
        fuenteInicial={fuente_activa}
        fondoInicial={fondo_activo}
        onGuardar={(nombre, fuente, fondo) => {
          setError(null);
          return guardarAjustesGenerales(nombre, fuente, fondo).catch((e: unknown) => {
            setError(e instanceof Error ? e.message : "Error inesperado.");
            throw e;
          });
        }}
      />

      <h2 className="cms-h2" style={{ marginBottom: "1rem" }}>Paletas predefinidas</h2>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
          gap: "1rem",
          marginBottom: "2.5rem",
        }}
      >
        {PALETAS_PREDEFINIDAS.map((p) => (
          <PaletaSwatch
            key={p.id}
            paleta={p}
            activa={paleta_activa === p.id}
            onSelect={() => ejecutar(() => activarPaleta(p.id))}
          />
        ))}
      </div>

      <h2 className="cms-h2" style={{ marginBottom: "1rem" }}>Paletas personalizadas</h2>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
          gap: "1rem",
          marginBottom: "2rem",
        }}
      >
        {personalizadas.map((p) => (
          <PaletaSwatch
            key={p.id}
            paleta={p}
            activa={paleta_activa === p.id}
            onSelect={() => ejecutar(() => activarPaleta(p.id))}
            onDelete={() => ejecutar(() => eliminarPaleta(p.id))}
          />
        ))}
        <FormNuevaPaleta
          onGuardar={(p) =>
            ejecutar(() => agregarPaleta({ id: p.id, nombre: p.nombre, colores: p.colores }))
          }
        />
      </div>

      <p className="cms-muted" style={{ fontSize: ".8rem" }}>
        Los cambios se aplican inmediatamente en todo el sitio.
      </p>
    </>
  );
}
