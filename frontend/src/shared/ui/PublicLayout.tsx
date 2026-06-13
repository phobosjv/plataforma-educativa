import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../../app/auth/AuthContext";

export function PublicLayout() {
  const { user } = useAuth();

  return (
    <div className="cms-shell">
      <nav className="cms-nav">
        <NavLink to="/" className="cms-nav-brand">
          Plataforma Educativa
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
      <main className="cms-main">
        <Outlet />
      </main>
      <footer className="cms-footer">
        Plataforma Educativa — contenidos para infantil y primaria
      </footer>
    </div>
  );
}
