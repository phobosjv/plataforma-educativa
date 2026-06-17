import { FormEvent, useEffect, useState } from "react";
import { useConfig, useConfigMutations } from "../../app/config/useConfig";
import { PALETAS_PREDEFINIDAS, type Palette } from "../../app/config/palettes";
import { FUENTES } from "../../app/config/fonts";
import { ESTILOS_FONDO, FONDOS, patronFondo } from "../../app/config/backgrounds";

// ── Ajustes generales: nombre del sitio + fuente + fondo ──────────────────────

function AjustesGenerales({
  nombreInicial,
  fuenteInicial,
  fondoInicial,
  estiloInicial,
  logoInicial,
  aulaLabelInicial,
  aulaEmojiInicial,
  onGuardar,
}: {
  nombreInicial: string;
  fuenteInicial: string;
  fondoInicial: string;
  estiloInicial: string;
  logoInicial: string;
  aulaLabelInicial: string;
  aulaEmojiInicial: string;
  onGuardar: (
    nombre: string,
    fuente: string,
    fondo: string,
    estilo: string,
    logo: string,
    aulaLabel: string,
    aulaEmoji: string,
  ) => Promise<void>;
}) {
  const [nombre, setNombre] = useState(nombreInicial);
  const [fuente, setFuente] = useState(fuenteInicial);
  const [fondo, setFondo] = useState(fondoInicial);
  const [estilo, setEstilo] = useState(estiloInicial);
  const [logo, setLogo] = useState(logoInicial);
  const [subiendoLogo, setSubiendoLogo] = useState(false);
  const [errorLogo, setErrorLogo] = useState<string | null>(null);
  const [aulaLabel, setAulaLabel] = useState(aulaLabelInicial);
  const [aulaEmoji, setAulaEmoji] = useState(aulaEmojiInicial);
  const [guardando, setGuardando] = useState(false);
  const [guardado, setGuardado] = useState(false);

  // Sincroniza si la config llega/actualiza desde el servidor.
  useEffect(() => setNombre(nombreInicial), [nombreInicial]);
  useEffect(() => setFuente(fuenteInicial), [fuenteInicial]);
  useEffect(() => setFondo(fondoInicial), [fondoInicial]);
  useEffect(() => setEstilo(estiloInicial), [estiloInicial]);
  useEffect(() => setLogo(logoInicial), [logoInicial]);
  useEffect(() => setAulaLabel(aulaLabelInicial), [aulaLabelInicial]);
  useEffect(() => setAulaEmoji(aulaEmojiInicial), [aulaEmojiInicial]);

  const sucio =
    nombre.trim() !== nombreInicial ||
    fuente !== fuenteInicial ||
    fondo !== fondoInicial ||
    estilo !== estiloInicial ||
    logo !== logoInicial ||
    aulaLabel.trim() !== aulaLabelInicial ||
    aulaEmoji !== aulaEmojiInicial;

  // Sube la imagen al propio origen (contexto MEDIA, content-addressed, sin SVG) y
  // guarda la URL devuelta como logo. No se persiste hasta pulsar "Guardar cambios".
  async function subirLogo(file: File) {
    setErrorLogo(null);
    setSubiendoLogo(true);
    try {
      const fd = new FormData();
      fd.append("fichero", file);
      const token = localStorage.getItem("auth_token");
      const r = await fetch("/api/v1/media/imagenes", {
        method: "POST",
        body: fd,
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (!r.ok) {
        const cuerpo = (await r.json().catch(() => null)) as { detail?: string } | null;
        throw new Error(cuerpo?.detail ?? "No se pudo subir el logo.");
      }
      const { url } = (await r.json()) as { url: string };
      setLogo(url);
      setGuardado(false);
    } catch (e) {
      setErrorLogo(e instanceof Error ? e.message : "Error al subir el logo.");
    } finally {
      setSubiendoLogo(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!nombre.trim() || !aulaLabel.trim() || guardando) return;
    setGuardando(true);
    setGuardado(false);
    onGuardar(nombre.trim(), fuente, fondo, estilo, logo, aulaLabel.trim(), aulaEmoji.trim())
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

      <label className="cms-label" style={{ display: "block", marginBottom: ".4rem" }}>
        Logo del sitio
      </label>
      <p className="cms-text-muted" style={{ marginBottom: ".6rem" }}>
        Imagen que acompaña al nombre en la cabecera (PNG, JPG, GIF o WebP, máx. 5 MB).
        Se recomienda un PNG con fondo transparente. Sin logo se muestra solo el nombre.
      </p>
      <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
        <div
          style={{
            width: 64,
            height: 64,
            borderRadius: "var(--cms-radius)",
            border: "1px solid var(--cms-color-border)",
            background: "var(--cms-color-surface)",
            display: "grid",
            placeItems: "center",
            overflow: "hidden",
            flexShrink: 0,
          }}
        >
          {logo ? (
            <img
              src={logo}
              alt="Logo del sitio"
              style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }}
            />
          ) : (
            <span className="cms-text-muted" style={{ fontSize: ".7rem" }}>sin logo</span>
          )}
        </div>
        <div style={{ display: "flex", gap: ".5rem", flexWrap: "wrap", alignItems: "center" }}>
          <label className="cms-btn cms-btn-ghost" style={{ cursor: subiendoLogo ? "wait" : "pointer", margin: 0 }}>
            {subiendoLogo ? "Subiendo…" : logo ? "Cambiar logo" : "Subir logo"}
            <input
              type="file"
              accept="image/png,image/jpeg,image/gif,image/webp"
              style={{ display: "none" }}
              disabled={subiendoLogo}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) subirLogo(file);
                e.target.value = "";
              }}
            />
          </label>
          {logo && (
            <button
              type="button"
              className="cms-btn cms-btn-ghost"
              onClick={() => { setLogo(""); setGuardado(false); }}
            >
              Quitar
            </button>
          )}
        </div>
      </div>
      {errorLogo && (
        <p role="alert" style={{ color: "var(--cms-color-danger)", fontSize: ".85rem", marginTop: "-1rem", marginBottom: "1.25rem" }}>
          {errorLogo}
        </p>
      )}

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
          const { url: patron, tile } = patronFondo(f.id, estilo);
          // En el preview (64px) mostramos ~la mitad del tile para que se aprecie el patrón.
          const maskSize = `${Math.round(tile / 2)}px ${Math.round(tile / 2)}px`;
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
                      WebkitMaskSize: maskSize,
                      maskSize: maskSize,
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

      <label className="cms-label" style={{ display: "block", marginBottom: ".6rem" }}>
        Disposición del estampado
      </label>
      <div
        style={{ display: "flex", gap: ".5rem", marginBottom: "1.5rem", flexWrap: "wrap" }}
        role="radiogroup"
        aria-label="Disposición del estampado"
      >
        {ESTILOS_FONDO.map((e) => {
          const activo = estilo === e.id;
          const deshabilitado = fondo === "ninguno";
          return (
            <button
              type="button"
              key={e.id}
              role="radio"
              aria-checked={activo}
              disabled={deshabilitado}
              onClick={() => { setEstilo(e.id); setGuardado(false); }}
              title={e.descripcion}
              style={{
                cursor: deshabilitado ? "not-allowed" : "pointer",
                opacity: deshabilitado ? 0.5 : 1,
                background: activo ? "var(--cms-color-primary)" : "var(--cms-color-surface)",
                color: activo ? "#fff" : "var(--cms-color-fg)",
                border: activo
                  ? "2px solid var(--cms-color-primary)"
                  : "1px solid var(--cms-color-border)",
                borderRadius: "var(--cms-radius)",
                padding: ".5rem .9rem",
                fontWeight: 600,
                fontSize: ".9rem",
              }}
            >
              {e.nombre}
              <span
                style={{
                  display: "block",
                  fontWeight: 400,
                  fontSize: ".75rem",
                  opacity: 0.85,
                }}
              >
                {e.descripcion}
              </span>
            </button>
          );
        })}
      </div>

      <label className="cms-label" style={{ display: "block", marginTop: "1.5rem", marginBottom: ".4rem" }}>
        Aula Abierta (asignaturas transversales)
      </label>
      <p className="cms-text-muted" style={{ marginBottom: ".6rem" }}>
        Nombre y emoji de la tarjeta que agrupa las asignaturas transversales (p. ej. Audición y
        Lenguaje) en el catálogo. Elige un término inclusivo para tu centro.
      </p>
      <div style={{ display: "flex", gap: ".75rem", flexWrap: "wrap", marginBottom: "1.25rem" }}>
        <div className="cms-form-group" style={{ marginBottom: 0, width: 90 }}>
          <label className="cms-label" htmlFor="cms-aula-emoji">Emoji</label>
          <input
            id="cms-aula-emoji"
            className="cms-input"
            value={aulaEmoji}
            maxLength={8}
            onChange={(e) => { setAulaEmoji(e.target.value); setGuardado(false); }}
            placeholder="🌟"
            style={{ textAlign: "center" }}
          />
        </div>
        <div className="cms-form-group" style={{ marginBottom: 0, flex: 1, minWidth: 220, maxWidth: 320 }}>
          <label className="cms-label" htmlFor="cms-aula-label">Nombre</label>
          <input
            id="cms-aula-label"
            className="cms-input"
            value={aulaLabel}
            maxLength={40}
            onChange={(e) => { setAulaLabel(e.target.value); setGuardado(false); }}
            placeholder="Aula Abierta"
            required
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
  const {
    nombre_sitio,
    fuente_activa,
    fondo_activo,
    fondo_estilo,
    logo_url,
    aula_abierta_label,
    aula_abierta_emoji,
    paleta_activa,
    personalizadas,
    isLoading,
  } = useConfig();
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
        estiloInicial={fondo_estilo}
        logoInicial={logo_url}
        aulaLabelInicial={aula_abierta_label}
        aulaEmojiInicial={aula_abierta_emoji}
        onGuardar={(nombre, fuente, fondo, estilo, logo, aulaLabel, aulaEmoji) => {
          setError(null);
          return guardarAjustesGenerales(
            nombre, fuente, fondo, estilo, logo, aulaLabel, aulaEmoji,
          ).catch((e: unknown) => {
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
