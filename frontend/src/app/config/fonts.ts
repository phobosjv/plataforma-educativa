// Catálogo de fuentes seleccionables para el sitio. Debe mantenerse alineado con
// FUENTES_PERMITIDAS del backend (contexto configuration) y con los @font-face de
// styles/fonts.css. Las fuentes (salvo "sistema") son self-hosted.

export interface Fuente {
  id: string;
  nombre: string;
  descripcion: string;
  categoria: "Sistema" | "Amigable" | "Legibilidad";
  // Pila CSS que se aplica a --cms-font cuando esta fuente está activa.
  stack: string;
}

const FALLBACK = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';

export const FUENTES: Fuente[] = [
  {
    id: "sistema",
    nombre: "Sistema",
    descripcion: "La fuente del dispositivo. Rápida, sin descargas.",
    categoria: "Sistema",
    stack: FALLBACK,
  },
  {
    id: "nunito",
    nombre: "Nunito",
    descripcion: "Redondeada y cálida. Acogedora para los más pequeños.",
    categoria: "Amigable",
    stack: `"Nunito", ${FALLBACK}`,
  },
  {
    id: "quicksand",
    nombre: "Quicksand",
    descripcion: "Geométrica y suave, con aire moderno.",
    categoria: "Amigable",
    stack: `"Quicksand", ${FALLBACK}`,
  },
  {
    id: "lexend",
    nombre: "Lexend",
    descripcion: "Diseñada para mejorar la fluidez de lectura.",
    categoria: "Legibilidad",
    stack: `"Lexend", ${FALLBACK}`,
  },
  {
    id: "atkinson",
    nombre: "Atkinson Hyperlegible",
    descripcion: "Máxima legibilidad, pensada para baja visión.",
    categoria: "Legibilidad",
    stack: `"Atkinson Hyperlegible", ${FALLBACK}`,
  },
  {
    id: "andika",
    nombre: "Andika",
    descripcion: "Creada para quienes aprenden a leer.",
    categoria: "Legibilidad",
    stack: `"Andika", ${FALLBACK}`,
  },
];

export const FUENTE_POR_DEFECTO = FUENTES[0];

export function resolverFuente(fuente_id: string): Fuente {
  return FUENTES.find((f) => f.id === fuente_id) ?? FUENTE_POR_DEFECTO;
}

export function aplicarFuente(fuente_id: string): void {
  const fuente = resolverFuente(fuente_id);
  document.documentElement.style.setProperty("--cms-font", fuente.stack);
}
