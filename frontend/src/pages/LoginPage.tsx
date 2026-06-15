import { FormEvent, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../app/auth/AuthContext";

export function LoginPage() {
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname ?? "/admin";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo iniciar sesión. Inténtalo de nuevo.",
      );
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: "4rem auto" }}>
      <h1 className="cms-h1" style={{ marginBottom: "1.5rem" }}>Acceder</h1>
      <form onSubmit={handleSubmit} noValidate>
        <div className="cms-form-group">
          <label className="cms-label" htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            className="cms-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
        </div>
        <div className="cms-form-group">
          <label className="cms-label" htmlFor="password">Contraseña</label>
          <input
            id="password"
            type="password"
            className="cms-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
        </div>
        {error && <p className="cms-error">{error}</p>}
        <button
          type="submit"
          className="cms-btn cms-btn-primary"
          disabled={isLoading}
          style={{ width: "100%", marginTop: "1rem", justifyContent: "center" }}
        >
          {isLoading ? "Accediendo…" : "Acceder"}
        </button>
      </form>
    </div>
  );
}
