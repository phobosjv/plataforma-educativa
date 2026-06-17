// Catálogo de redes sociales soportadas + sus iconos (SVG inline self-hosted, sin CDN
// externo por la privacidad de los menores, §10). Los IDs deben coincidir con
// REDES_SOCIALES_PERMITIDAS del backend (configuration/domain/model.py).

export type RedSocialId =
  | "facebook"
  | "instagram"
  | "x"
  | "youtube"
  | "tiktok"
  | "whatsapp"
  | "telegram"
  | "linkedin";

export interface RedSocialDef {
  id: RedSocialId;
  label: string;
  color: string; // color de marca (fondo del badge)
  placeholder: string;
  // Dominios (sin "www.") que identifican esta red en un enlace del cuerpo de un artículo.
  hosts: string[];
}

export const REDES_SOCIALES: RedSocialDef[] = [
  { id: "facebook", label: "Facebook", color: "#1877F2", placeholder: "https://facebook.com/tu-pagina", hosts: ["facebook.com", "fb.com", "fb.me", "m.facebook.com"] },
  { id: "instagram", label: "Instagram", color: "#E4405F", placeholder: "https://instagram.com/tu-perfil", hosts: ["instagram.com", "instagr.am"] },
  { id: "x", label: "X (Twitter)", color: "#000000", placeholder: "https://x.com/tu-perfil", hosts: ["x.com", "twitter.com", "mobile.twitter.com"] },
  { id: "youtube", label: "YouTube", color: "#FF0000", placeholder: "https://youtube.com/@tu-canal", hosts: ["youtube.com", "m.youtube.com", "youtu.be"] },
  { id: "tiktok", label: "TikTok", color: "#000000", placeholder: "https://tiktok.com/@tu-perfil", hosts: ["tiktok.com", "vm.tiktok.com"] },
  { id: "whatsapp", label: "WhatsApp", color: "#25D366", placeholder: "https://wa.me/34600000000", hosts: ["wa.me", "whatsapp.com", "api.whatsapp.com", "chat.whatsapp.com"] },
  { id: "telegram", label: "Telegram", color: "#229ED9", placeholder: "https://t.me/tu-canal", hosts: ["t.me", "telegram.me", "telegram.org"] },
  { id: "linkedin", label: "LinkedIn", color: "#0A66C2", placeholder: "https://linkedin.com/company/tu-empresa", hosts: ["linkedin.com", "lnkd.in"] },
];

export function defRed(id: string): RedSocialDef | undefined {
  return REDES_SOCIALES.find((r) => r.id === id);
}

// Identifica a qué red social pertenece una URL por su dominio (insensible a "www." y a
// subdominios). Devuelve undefined si no es una red conocida. Se usa para decorar con su
// icono los enlaces a redes que un editor inserta en el cuerpo de un artículo.
export function detectarRed(url: string): RedSocialId | undefined {
  let host: string;
  try {
    host = new URL(url, "https://x.invalid").hostname.toLowerCase().replace(/^www\./, "");
  } catch {
    return undefined;
  }
  const red = REDES_SOCIALES.find((r) =>
    r.hosts.some((h) => host === h || host.endsWith("." + h)),
  );
  return red?.id;
}

// Marcado SVG (cadena) del glifo blanco de cada red sobre su badge de color. Fuente ÚNICA de
// los iconos: la usa tanto el componente React `IconoRed` como el generador de string
// `iconoRedSVG` (decoración de enlaces en artículos). Atributos en nomenclatura SVG (kebab).
const GLIFOS: Record<RedSocialId, string> = {
  facebook: '<text x="12" y="17.5" text-anchor="middle" font-size="15" font-weight="700" fill="#fff" font-family="Georgia, serif">f</text>',
  linkedin: '<text x="12" y="16.5" text-anchor="middle" font-size="9.5" font-weight="700" fill="#fff" font-family="Arial, sans-serif">in</text>',
  x: '<text x="12" y="17" text-anchor="middle" font-size="13" font-weight="700" fill="#fff" font-family="Arial, sans-serif">X</text>',
  youtube: '<polygon points="9.5,8 17,12 9.5,16" fill="#fff" />',
  telegram: '<polygon points="5,12 19,6 16.5,18 11,14.5 9,17 9,13.5 16,9 8.5,12.5" fill="#fff" />',
  instagram:
    '<rect x="6.5" y="6.5" width="11" height="11" rx="3.2" fill="none" stroke="#fff" stroke-width="1.6" />' +
    '<circle cx="12" cy="12" r="3" fill="none" stroke="#fff" stroke-width="1.6" />' +
    '<circle cx="15.4" cy="8.6" r="1" fill="#fff" />',
  whatsapp:
    '<path d="M6 18l1-3a6 6 0 1 1 2 2z" fill="none" stroke="#fff" stroke-width="1.6" stroke-linejoin="round" />' +
    '<path d="M10.5 10.5c0 3 2 5 5 5 .6 0 1-.6 1-.6l-1.4-1-1 .7c-1-.4-1.7-1.1-2.1-2.1l.7-1-1-1.4s-.6.4-.6 1z" fill="#fff" />',
  tiktok:
    '<circle cx="10" cy="15.5" r="2.4" fill="none" stroke="#fff" stroke-width="1.6" />' +
    '<path d="M12.4 15.5V7c.6 2 2 3 3.6 3.1" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />',
};

// Contenido interno del SVG (badge + glifo) para un id dado.
function interiorBadge(id: string, color: string): string {
  const glifo = GLIFOS[id as RedSocialId] ?? '<text x="12" y="16.5" text-anchor="middle" font-size="10" font-weight="700" fill="#fff">?</text>';
  return `<rect x="0" y="0" width="24" height="24" rx="6" fill="${color}" />${glifo}`;
}

export function IconoRed({ id, size = 28 }: { id: string; size?: number }) {
  const color = defRed(id)?.color ?? "#64748b";
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      role="img"
      aria-hidden
      focusable="false"
      dangerouslySetInnerHTML={{ __html: interiorBadge(id, color) }}
    />
  );
}

// Versión en cadena del icono (para inyectar en HTML ya saneado: decoración de enlaces a
// redes en el cuerpo de un artículo, ver ContenidoPage). El badge se construye en código de
// confianza, no proviene del HTML del usuario.
export function iconoRedSVG(id: string, size = 18): string {
  const color = defRed(id)?.color ?? "#64748b";
  return (
    `<svg width="${size}" height="${size}" viewBox="0 0 24 24" role="img" aria-hidden="true" ` +
    `focusable="false" class="cms-prose-red-icon">${interiorBadge(id, color)}</svg>`
  );
}
