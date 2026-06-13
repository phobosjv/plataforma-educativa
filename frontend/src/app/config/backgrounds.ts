// Catálogo de fondos/estampados temáticos. Debe mantenerse alineado con
// FONDOS_PERMITIDOS del backend. Cada fondo (salvo "ninguno") es un patrón SVG
// self-hosted en /patterns/<id>.svg que se recolorea con la paleta activa
// mediante una máscara CSS (ver styles/tokens.css, regla body::before).

export interface Fondo {
  id: string;
  nombre: string;
  descripcion: string;
}

export const FONDOS: Fondo[] = [
  { id: "ninguno", nombre: "Ninguno", descripcion: "Fondo liso, sin estampado." },
  { id: "classroom", nombre: "Aula", descripcion: "Pizarra, lápiz, reloj, regla…" },
  { id: "naturaleza", nombre: "Naturaleza", descripcion: "Pino, hoja, seta, bellota…" },
  { id: "espacio", nombre: "Espacio", descripcion: "Cohete, planeta, estrella, luna…" },
  { id: "oceano", nombre: "Océano", descripcion: "Pez, concha, burbujas, estrella de mar…" },
  { id: "geometrico", nombre: "Geométrico", descripcion: "Formas y lunares, neutro." },
  { id: "granja", nombre: "Granja", descripcion: "Granero, trigo, valla, sol…" },
];

// Opacidad del estampado: sutil para no afectar a la legibilidad de los menores.
export const OPACIDAD_FONDO = 0.07;

export function resolverFondo(fondo_id: string): Fondo {
  return FONDOS.find((f) => f.id === fondo_id) ?? FONDOS[0];
}

export function urlPatron(fondo_id: string): string | null {
  return fondo_id === "ninguno" ? null : `/patterns/${fondo_id}.svg`;
}

export function aplicarFondo(fondo_id: string): void {
  const root = document.documentElement;
  const url = urlPatron(fondo_id);
  if (!url) {
    root.style.setProperty("--cms-bg-pattern", "none");
    root.style.setProperty("--cms-bg-opacity", "0");
    return;
  }
  root.style.setProperty("--cms-bg-pattern", `url("${url}")`);
  root.style.setProperty("--cms-bg-opacity", String(OPACIDAD_FONDO));
}
