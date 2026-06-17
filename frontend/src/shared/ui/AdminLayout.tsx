import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../../app/auth/AuthContext";
import { useConfig } from "../../app/config/useConfig";

export function AdminLayout() {
  const { user, logout } = useAuth();
  const { nombre_sitio, logo_url } = useConfig();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="cms-admin-shell">
      <aside className="cms-sidebar">
        <div className="cms-sidebar-brand">
          {logo_url && (
            <img src={logo_url} alt="" className="cms-nav-logo" aria-hidden />
          )}
          {nombre_sitio}
        </div>
        <NavLink
          to="/admin"
          end
          className={({ isActive }) =>
            "cms-sidebar-link" + (isActive ? " cms-sidebar-link-active" : "")
          }
        >
          Inicio
        </NavLink>
        <NavLink
          to="/admin/contenidos"
          className={({ isActive }) =>
            "cms-sidebar-link" + (isActive ? " cms-sidebar-link-active" : "")
          }
        >
          Contenidos
        </NavLink>
        <NavLink
          to="/admin/taxonomia"
          className={({ isActive }) =>
            "cms-sidebar-link" + (isActive ? " cms-sidebar-link-active" : "")
          }
        >
          Taxonomía
        </NavLink>
        <NavLink
          to="/admin/configuracion"
          className={({ isActive }) =>
            "cms-sidebar-link" + (isActive ? " cms-sidebar-link-active" : "")
          }
        >
          Apariencia
        </NavLink>
        {user?.rol === "admin" && (
          <>
            <NavLink
              to="/admin/usuarios"
              className={({ isActive }) =>
                "cms-sidebar-link" + (isActive ? " cms-sidebar-link-active" : "")
              }
            >
              Usuarios
            </NavLink>
            <NavLink
              to="/admin/copias"
              className={({ isActive }) =>
                "cms-sidebar-link" + (isActive ? " cms-sidebar-link-active" : "")
              }
            >
              Copias de seguridad
            </NavLink>
          </>
        )}
        <div className="cms-sidebar-spacer" />
        <Link to="/" className="cms-sidebar-link cms-sidebar-link-web">
          ↗ Ver la web
        </Link>
        <button className="cms-sidebar-logout" onClick={handleLogout}>
          Cerrar sesión
        </button>
      </aside>
      <div className="cms-admin-content">
        <Outlet />
      </div>
    </div>
  );
}
