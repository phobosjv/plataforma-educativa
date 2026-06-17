import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../app/auth/AuthContext";
import { useConfig } from "../../app/config/useConfig";
import { IconoRed, defRed } from "../../app/config/redesSociales";

export function PublicLayout() {
  const { user } = useAuth();
  const {
    nombre_sitio,
    logo_url,
    donaciones,
    redes_sociales,
    publicidad_activa,
    publicidad_html_izquierda,
    publicidad_html_derecha,
  } = useConfig();
  const { pathname } = useLocation();

  // La publicidad (zona de adultos, §10) solo se muestra en las pantallas de navegación del
  // catálogo (ruta "/"). NUNCA durante un ejercicio/artículo (/contenido/:id, lo usa un menor)
  // ni en el login, ni en el panel admin (que usa otro layout).
  const enCatalogo = pathname === "/";
  const mostrarPublicidad = publicidad_activa && enCatalogo;

  return (
    <div className="cms-shell">
      <nav className="cms-nav">
        <NavLink to="/" className="cms-nav-brand">
          {logo_url && (
            <img src={logo_url} alt="" className="cms-nav-logo" aria-hidden />
          )}
          {nombre_sitio}
        </NavLink>
        <span className="cms-nav-spacer" />
        <NavLink
          to="/"
          className={({ isActive }) =>
            "cms-nav-link" + (isActive ? " cms-nav-link-active" : "")
          }
          end
        >
          Catálogo
        </NavLink>
        {user ? (
          <NavLink to="/admin" className="cms-nav-link">
            Panel admin
          </NavLink>
        ) : (
          <NavLink
            to="/login"
            className={({ isActive }) =>
              "cms-nav-link" + (isActive ? " cms-nav-link-active" : "")
            }
          >
            Acceder
          </NavLink>
        )}
      </nav>

      {mostrarPublicidad && publicidad_html_izquierda && (
        <aside
          className="cms-ad-rail cms-ad-rail-left"
          aria-label="Publicidad"
          dangerouslySetInnerHTML={{ __html: publicidad_html_izquierda }}
        />
      )}
      {mostrarPublicidad && publicidad_html_derecha && (
        <aside
          className="cms-ad-rail cms-ad-rail-right"
          aria-label="Publicidad"
          dangerouslySetInnerHTML={{ __html: publicidad_html_derecha }}
        />
      )}

      <main className="cms-main">
        <Outlet />
      </main>
      <footer className="cms-footer">
        {redes_sociales.length > 0 && (
          <div className="cms-footer-redes">
            {redes_sociales.map((r, i) => (
              <a
                key={i}
                href={r.url}
                className="cms-footer-red"
                target="_blank"
                rel="noopener noreferrer external"
                title={defRed(r.red)?.label ?? r.red}
                aria-label={defRed(r.red)?.label ?? r.red}
              >
                <IconoRed id={r.red} />
              </a>
            ))}
          </div>
        )}
        <div>{nombre_sitio} — contenidos para infantil y primaria</div>
        {donaciones.length > 0 && (
          <div className="cms-footer-donaciones">
            <span className="cms-text-muted">¿Te gusta el proyecto? Puedes apoyarlo:</span>
            {donaciones.map((d, i) => (
              <a
                key={i}
                href={d.url}
                className="cms-btn cms-btn-ghost cms-btn-sm"
                target="_blank"
                rel="noopener noreferrer external"
              >
                ❤ {d.etiqueta}
              </a>
            ))}
          </div>
        )}
      </footer>
    </div>
  );
}
