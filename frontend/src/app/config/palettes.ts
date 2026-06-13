export interface PaletteColors {
  bg: string;
  surface: string;
  fg: string;
  primary: string;
}

export interface Palette {
  id: string;
  nombre: string;
  predefinida: boolean;
  emoji: string;
  colores: PaletteColors;
}

export const PALETAS_PREDEFINIDAS: Palette[] = [
  {
    id: "cielo",
    nombre: "Cielo Azul",
    predefinida: true,
    emoji: "☁️",
    colores: { bg: "#e0f7ff", surface: "#ffffff", fg: "#0a4a6e", primary: "#0284c7" },
  },
  {
    id: "bosque",
    nombre: "Bosque Mágico",
    predefinida: true,
    emoji: "🌿",
    colores: { bg: "#e8f5e9", surface: "#ffffff", fg: "#1b5e20", primary: "#2e7d32" },
  },
  {
    id: "coral",
    nombre: "Coral Feliz",
    predefinida: true,
    emoji: "🌸",
    colores: { bg: "#fce4ec", surface: "#ffffff", fg: "#880e4f", primary: "#e91e63" },
  },
  {
    id: "sol",
    nombre: "Sol Brillante",
    predefinida: true,
    emoji: "☀️",
    colores: { bg: "#fff8e1", surface: "#ffffff", fg: "#e65100", primary: "#f59e0b" },
  },
  {
    id: "lavanda",
    nombre: "Lavanda Soñadora",
    predefinida: true,
    emoji: "🦄",
    colores: { bg: "#f3e5f5", surface: "#ffffff", fg: "#4a148c", primary: "#9c27b0" },
  },
  {
    id: "estandar",
    nombre: "Estándar",
    predefinida: true,
    emoji: "📚",
    colores: { bg: "#f8fafc", surface: "#ffffff", fg: "#1f2937", primary: "#4f46e5" },
  },
];

// Mezcla paletas predefinidas con personalizadas y devuelve la activa
export function resolverPaleta(
  paleta_activa: string,
  paletas_personalizadas: Palette[],
): PaletteColors {
  const todas = [...PALETAS_PREDEFINIDAS, ...paletas_personalizadas];
  return (todas.find((p) => p.id === paleta_activa) ?? PALETAS_PREDEFINIDAS[0]).colores;
}

export function aplicarPaleta(colores: PaletteColors): void {
  const root = document.documentElement;
  root.style.setProperty("--cms-color-bg", colores.bg);
  root.style.setProperty("--cms-color-surface", colores.surface);
  root.style.setProperty("--cms-color-fg", colores.fg);
  root.style.setProperty("--cms-color-primary", colores.primary);
  root.style.setProperty("--cms-color-primary-hover", darken(colores.primary, 12));
  root.style.setProperty("--cms-color-muted", hexWithOpacity(colores.fg, 0.55));
  root.style.setProperty("--cms-color-border", hexWithOpacity(colores.fg, 0.14));
}

function darken(hex: string, pct: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  const f = 1 - pct / 100;
  return (
    "#" +
    [r, g, b]
      .map((c) => Math.round(Math.max(0, c * f)).toString(16).padStart(2, "0"))
      .join("")
  );
}

function hexWithOpacity(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}
