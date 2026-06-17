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
}

export const REDES_SOCIALES: RedSocialDef[] = [
  { id: "facebook", label: "Facebook", color: "#1877F2", placeholder: "https://facebook.com/tu-pagina" },
  { id: "instagram", label: "Instagram", color: "#E4405F", placeholder: "https://instagram.com/tu-perfil" },
  { id: "x", label: "X (Twitter)", color: "#000000", placeholder: "https://x.com/tu-perfil" },
  { id: "youtube", label: "YouTube", color: "#FF0000", placeholder: "https://youtube.com/@tu-canal" },
  { id: "tiktok", label: "TikTok", color: "#000000", placeholder: "https://tiktok.com/@tu-perfil" },
  { id: "whatsapp", label: "WhatsApp", color: "#25D366", placeholder: "https://wa.me/34600000000" },
  { id: "telegram", label: "Telegram", color: "#229ED9", placeholder: "https://t.me/tu-canal" },
  { id: "linkedin", label: "LinkedIn", color: "#0A66C2", placeholder: "https://linkedin.com/company/tu-empresa" },
];

export function defRed(id: string): RedSocialDef | undefined {
  return REDES_SOCIALES.find((r) => r.id === id);
}

// Glifo blanco de cada red (sobre el badge de color de marca). Coordenadas en un viewBox 0 0 24 24.
function glifo(id: string) {
  switch (id) {
    case "facebook":
      return <text x="12" y="17.5" textAnchor="middle" fontSize="15" fontWeight="700" fill="#fff" fontFamily="Georgia, serif">f</text>;
    case "linkedin":
      return <text x="12" y="16.5" textAnchor="middle" fontSize="9.5" fontWeight="700" fill="#fff" fontFamily="Arial, sans-serif">in</text>;
    case "x":
      return <text x="12" y="17" textAnchor="middle" fontSize="13" fontWeight="700" fill="#fff" fontFamily="Arial, sans-serif">X</text>;
    case "youtube":
      return <polygon points="9.5,8 17,12 9.5,16" fill="#fff" />;
    case "telegram":
      return <polygon points="5,12 19,6 16.5,18 11,14.5 9,17 9,13.5 16,9 8.5,12.5" fill="#fff" />;
    case "instagram":
      return (
        <>
          <rect x="6.5" y="6.5" width="11" height="11" rx="3.2" fill="none" stroke="#fff" strokeWidth="1.6" />
          <circle cx="12" cy="12" r="3" fill="none" stroke="#fff" strokeWidth="1.6" />
          <circle cx="15.4" cy="8.6" r="1" fill="#fff" />
        </>
      );
    case "whatsapp":
      return (
        <>
          <path d="M6 18l1-3a6 6 0 1 1 2 2z" fill="none" stroke="#fff" strokeWidth="1.6" strokeLinejoin="round" />
          <path d="M10.5 10.5c0 3 2 5 5 5 .6 0 1-.6 1-.6l-1.4-1-1 .7c-1-.4-1.7-1.1-2.1-2.1l.7-1-1-1.4s-.6.4-.6 1z" fill="#fff" />
        </>
      );
    case "tiktok":
      return (
        <>
          <circle cx="10" cy="15.5" r="2.4" fill="none" stroke="#fff" strokeWidth="1.6" />
          <path d="M12.4 15.5V7c.6 2 2 3 3.6 3.1" fill="none" stroke="#fff" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </>
      );
    default:
      return <text x="12" y="16.5" textAnchor="middle" fontSize="10" fontWeight="700" fill="#fff">?</text>;
  }
}

export function IconoRed({ id, size = 28 }: { id: string; size?: number }) {
  const def = defRed(id);
  const color = def?.color ?? "#64748b";
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      role="img"
      aria-hidden
      focusable="false"
    >
      <rect x="0" y="0" width="24" height="24" rx="6" fill={color} />
      {glifo(id)}
    </svg>
  );
}
