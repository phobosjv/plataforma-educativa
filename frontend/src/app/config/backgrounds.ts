// Catálogo de fondos/estampados temáticos. Debe mantenerse alineado con
// FONDOS_PERMITIDOS del backend. Cada fondo (salvo "ninguno") es un patrón SVG
// que se recolorea con la paleta activa mediante una máscara CSS (ver
// styles/tokens.css, regla body::before).
//
// Dos disposiciones (fondo_estilo):
//   - "ordenado":    usa el tile fijo self-hosted en /patterns/<id>.svg (4 iconos en rejilla).
//   - "desordenado": genera un patrón disperso a partir de los mismos iconos, con posición,
//                    rotación y escala variables, de modo que DOS ICONOS IGUALES NUNCA quedan
//                    adyacentes (ni dentro del tile ni al repetirse: la selección es toroidal).

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

export interface EstiloFondo {
  id: "ordenado" | "desordenado";
  nombre: string;
  descripcion: string;
}

export const ESTILOS_FONDO: EstiloFondo[] = [
  { id: "ordenado", nombre: "Ordenada", descripcion: "Iconos en rejilla regular." },
  { id: "desordenado", nombre: "Desordenada", descripcion: "Iconos dispersos, sin dos iguales seguidos." },
];

// Opacidad del estampado: sutil para no afectar a la legibilidad de los menores.
export const OPACIDAD_FONDO = 0.07;

// ── Iconos (glifos) por tema, en coordenadas locales (~ caja 0..64). Son los
// mismos dibujos de /patterns/<id>.svg, sin la traslación de colocación, para poder
// recomponerlos de forma dispersa. ────────────────────────────────────────────────
const GLYPHS: Record<string, string[]> = {
  classroom: [
    '<rect x="0" y="0" width="20" height="58" rx="3"/><path d="M0 58 L10 76 L20 58"/><line x1="0" y1="14" x2="20" y2="14"/>',
    '<path d="M0 8 C12 0 28 0 38 6 C48 0 64 0 76 8 L76 50 C64 42 48 42 38 48 C28 42 12 42 0 50 Z"/><line x1="38" y1="6" x2="38" y2="48"/>',
    '<circle cx="28" cy="28" r="26"/><path d="M28 12 L28 28 L40 36"/>',
    '<rect x="0" y="0" width="64" height="22" rx="3"/><line x1="12" y1="0" x2="12" y2="10"/><line x1="24" y1="0" x2="24" y2="10"/><line x1="36" y1="0" x2="36" y2="10"/><line x1="48" y1="0" x2="48" y2="10"/>',
  ],
  naturaleza: [
    '<path d="M28 0 L48 32 L8 32 Z"/><path d="M28 20 L54 56 L2 56 Z"/><line x1="28" y1="56" x2="28" y2="72"/>',
    '<path d="M0 42 C0 12 30 0 52 0 C52 30 30 50 0 42 Z"/><path d="M8 40 L46 8"/>',
    '<path d="M2 26 C2 8 18 0 30 0 C42 0 58 8 58 26 Z"/><path d="M18 26 C18 44 14 52 22 58 L38 58 C46 52 42 44 42 26"/>',
    '<path d="M6 14 C6 6 14 2 26 2 C38 2 46 6 46 14 Z"/><path d="M10 14 C10 34 18 46 26 46 C34 46 42 34 42 14"/><line x1="26" y1="2" x2="26" y2="-6"/>',
  ],
  espacio: [
    '<path d="M24 0 C40 14 40 40 30 56 L18 56 C8 40 8 14 24 0 Z"/><circle cx="24" cy="24" r="8"/><path d="M18 50 L6 64 L16 58 Z"/><path d="M30 50 L42 64 L32 58 Z"/>',
    '<circle cx="28" cy="28" r="20"/><ellipse cx="28" cy="28" rx="38" ry="11" transform="rotate(-20 28 28)"/>',
    '<path d="M28 4 L35 22 L54 22 L39 34 L45 54 L28 42 L11 54 L17 34 L2 22 L21 22 Z"/>',
    '<path d="M40 4 C20 6 8 22 10 40 C12 56 28 64 44 58 C30 54 22 42 22 30 C22 18 30 8 40 4 Z"/>',
  ],
  oceano: [
    '<path d="M0 24 C16 4 52 4 68 24 C52 44 16 44 0 24 Z"/><path d="M68 24 L86 10 L82 24 L86 38 Z"/><circle cx="20" cy="20" r="3" fill="#000"/>',
    '<path d="M28 56 C2 56 0 24 28 4 C56 24 54 56 28 56 Z"/><path d="M28 56 L16 16 M28 56 L28 8 M28 56 L40 16"/>',
    '<circle cx="14" cy="42" r="12"/><circle cx="38" cy="22" r="9"/><circle cx="22" cy="8" r="6"/>',
    '<path d="M30 4 L40 24 L60 27 L45 42 L49 62 L30 52 L11 62 L15 42 L0 27 L20 24 Z"/>',
  ],
  geometrico: [
    '<circle cx="28" cy="28" r="24"/>',
    '<path d="M30 0 L60 50 L0 50 Z"/>',
    '<path d="M0 20 C18 0 38 40 58 20 C78 0 98 40 118 20"/>',
    '<rect x="0" y="0" width="36" height="36" rx="8" transform="rotate(15 18 18)"/>',
    '<circle cx="6" cy="6" r="5" fill="#000"/><circle cx="26" cy="14" r="5" fill="#000"/><circle cx="14" cy="28" r="5" fill="#000"/>',
  ],
  granja: [
    '<path d="M4 24 L4 64 L60 64 L60 24"/><path d="M0 24 L32 2 L64 24"/><rect x="24" y="40" width="16" height="24"/>',
    '<line x1="14" y1="22" x2="14" y2="66"/><path d="M14 22 C5 24 3 13 8 6 C15 9 17 16 14 22 Z"/><path d="M14 22 C23 24 25 13 20 6 C13 9 11 16 14 22 Z"/><path d="M14 38 C6 40 4 30 8 24 M14 38 C22 40 24 30 20 24"/>',
    '<path d="M6 8 L6 50 M22 8 L22 50 M38 8 L38 50 M54 8 L54 50"/><path d="M0 20 L60 20 M0 36 L60 36"/><path d="M6 8 L6 2 M22 8 L22 2 M38 8 L38 2 M54 8 L54 2"/>',
    '<circle cx="28" cy="28" r="15"/><path d="M28 2 L28 -5 M28 53 L28 60 M2 28 L-5 28 M53 28 L60 28 M11 11 L5 5 M45 45 L51 51 M45 11 L51 5 M11 45 L5 51"/>',
  ],
};

// PRNG determinista (mulberry32): el patrón es estable entre recargas y entre usuarios.
function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function hashSeed(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

const COLS = 5;
const ROWS = 5;
const CELL = 96;
const DISORDER_TILE = COLS * CELL; // 480px

// Iconos prohibidos para la celda (r,c): su vecino izquierdo y superior, más —en los
// bordes— el de la columna 0 / fila 0 (costura toroidal), de modo que al repetir el tile
// dos iconos iguales nunca queden adyacentes. Asume relleno en orden row-major.
function vecinosProhibidos(grid: number[][], r: number, c: number): Set<number> {
  const p = new Set<number>();
  if (c > 0) p.add(grid[r][c - 1]);
  if (r > 0) p.add(grid[r - 1][c]);
  if (c === COLS - 1) p.add(grid[r][0]);
  if (r === ROWS - 1) p.add(grid[0][c]);
  return p;
}

function tieneColisionToroidal(grid: number[][]): boolean {
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      if (grid[r][c] === grid[r][(c + 1) % COLS]) return true;
      if (grid[r][c] === grid[(r + 1) % ROWS][c]) return true;
    }
  }
  return false;
}

// Llenado voraz aleatorio (puede fallar la esquina con pocos iconos; se reintenta fuera).
function construirGrid(rnd: () => number, n: number): number[][] {
  const grid: number[][] = [];
  for (let r = 0; r < ROWS; r++) {
    grid[r] = [];
    for (let c = 0; c < COLS; c++) {
      const prohib = vecinosProhibidos(grid, r, c);
      let idx = Math.floor(rnd() * n);
      for (let t = 0; prohib.has(idx) && t < 50; t++) idx = Math.floor(rnd() * n);
      grid[r][c] = idx;
    }
  }
  return grid;
}

// Respaldo determinista por backtracking: garantiza una rejilla sin colisiones si existe
// (existe para n>=3 en una rejilla 5x5 toroidal). Solo se usa si el azar no la encontró.
function gridSeguro(n: number): number[][] {
  const grid: number[][] = Array.from({ length: ROWS }, () => Array<number>(COLS).fill(-1));
  const resolver = (pos: number): boolean => {
    if (pos === ROWS * COLS) return true;
    const r = Math.floor(pos / COLS);
    const c = pos % COLS;
    const prohib = vecinosProhibidos(grid, r, c);
    for (let v = 0; v < n; v++) {
      if (prohib.has(v)) continue;
      grid[r][c] = v;
      if (resolver(pos + 1)) return true;
      grid[r][c] = -1;
    }
    return false;
  };
  resolver(0);
  return grid;
}

const _cache = new Map<string, string>();

// Genera el tile disperso como data-URI SVG. Cada celda recibe un icono elegido para
// que difiera de su vecino izquierdo y superior; además es TOROIDAL (la última columna
// difiere de la primera y la última fila de la primera), así al repetir el tile dos
// iconos iguales nunca quedan adyacentes en los bordes.
function generarPatronDesordenado(fondo_id: string): string | null {
  const cacheado = _cache.get(fondo_id);
  if (cacheado) return cacheado;

  const glyphs = GLYPHS[fondo_id];
  if (!glyphs || glyphs.length < 2) return null;

  const n = glyphs.length;
  const baseSeed = hashSeed(fondo_id);
  // Se reintenta con semillas distintas hasta lograr una rejilla SIN colisiones
  // toroidales. Con pocos iconos (n=4) el llenado voraz a veces atrapa la esquina,
  // pero existen coloraciones válidas y unas pocas semillas dan con una.
  let grid = construirGrid(mulberry32(baseSeed), n);
  for (let intento = 1; intento <= 60 && tieneColisionToroidal(grid); intento++) {
    grid = construirGrid(mulberry32(baseSeed + intento * 0x9e3779b1), n);
  }
  // Respaldo determinista garantizado por construcción (base latina) si, muy
  // improbablemente, no se encontró una rejilla limpia al azar.
  if (tieneColisionToroidal(grid)) grid = gridSeguro(n);

  const rnd = mulberry32(baseSeed ^ 0x5bd1e995);
  let celdas = "";
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const jx = (rnd() - 0.5) * CELL * 0.34;
      const jy = (rnd() - 0.5) * CELL * 0.34;
      const rot = Math.floor(rnd() * 360);
      const esc = (0.7 + rnd() * 0.45).toFixed(2);
      const cx = (c * CELL + CELL / 2 + jx).toFixed(1);
      const cy = (r * CELL + CELL / 2 + jy).toFixed(1);
      // translate(-30 -32) centra aproximadamente el glifo (caja local ~0..64).
      celdas += `<g transform="translate(${cx} ${cy}) rotate(${rot}) scale(${esc}) translate(-30 -32)">${glyphs[grid[r][c]]}</g>`;
    }
  }

  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${DISORDER_TILE} ${DISORDER_TILE}" ` +
    `width="${DISORDER_TILE}" height="${DISORDER_TILE}">` +
    `<g fill="none" stroke="#000" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">${celdas}</g></svg>`;
  const url = `data:image/svg+xml,${encodeURIComponent(svg)}`;
  _cache.set(fondo_id, url);
  return url;
}

// Resuelve el patrón (url de máscara y tamaño de tile) para un fondo y estilo dados.
export function patronFondo(
  fondo_id: string,
  estilo: string = "ordenado",
): { url: string | null; tile: number } {
  if (fondo_id === "ninguno") return { url: null, tile: 240 };
  if (estilo === "desordenado") {
    const data = generarPatronDesordenado(fondo_id);
    if (data) return { url: data, tile: DISORDER_TILE };
  }
  return { url: `/patterns/${fondo_id}.svg`, tile: 240 };
}

export function resolverFondo(fondo_id: string): Fondo {
  return FONDOS.find((f) => f.id === fondo_id) ?? FONDOS[0];
}

export function aplicarFondo(fondo_id: string, estilo: string = "ordenado"): void {
  const root = document.documentElement;
  const { url, tile } = patronFondo(fondo_id, estilo);
  if (!url) {
    root.style.setProperty("--cms-bg-pattern", "none");
    root.style.setProperty("--cms-bg-opacity", "0");
    return;
  }
  root.style.setProperty("--cms-bg-pattern", `url("${url}")`);
  root.style.setProperty("--cms-bg-opacity", String(OPACIDAD_FONDO));
  root.style.setProperty("--cms-bg-size", `${tile}px ${tile}px`);
}
