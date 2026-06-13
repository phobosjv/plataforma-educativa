import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { api } from "../../shared/api/client";
import type { components } from "../../shared/api/schema";

type Usuario = components["schemas"]["UsuarioResponse"];

function fetchUsuarios(): Promise<Usuario[]> {
  return api.GET("/api/v1/users/").then(({ data, error }) => {
    if (error) throw new Error("Sin acceso");
    return data ?? [];
  });
}

export function UsuariosPage() {
  const qc = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["usuarios"],
    queryFn: fetchUsuarios,
  });

  const crearUsuario = useMutation({
    mutationFn: (body: components["schemas"]["CrearUsuarioRequest"]) =>
      api.POST("/api/v1/users/", { body }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["usuarios"] });
      setForm({ email: "", password: "", rol: "editor" });
    },
  });

  const [form, setForm] = useState({ email: "", password: "", rol: "editor" as "admin" | "editor" });
  const [error, setError] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    crearUsuario.mutate(form, {
      onError: () => setError("No se pudo crear el usuario. ¿El email ya existe?"),
    });
  }

  return (
    <>
      <div className="cms-admin-header">
        <h1 className="cms-h1">Usuarios</h1>
      </div>

      {isLoading ? (
        <div className="cms-spinner" role="status" aria-label="Cargando" />
      ) : isError ? (
        <p className="cms-error">No tienes permisos para ver los usuarios.</p>
      ) : (
        <table className="cms-table" style={{ marginBottom: "2rem" }}>
          <thead>
            <tr>
              <th>Email</th>
              <th>Rol</th>
              <th>Activo</th>
            </tr>
          </thead>
          <tbody>
            {data?.map((u) => (
              <tr key={u.id}>
                <td>{u.email}</td>
                <td>
                  <span className={`cms-badge cms-badge-${u.rol === "admin" ? "publicado" : "texto"}`}>
                    {u.rol}
                  </span>
                </td>
                <td>{u.activo ? "Sí" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h2 className="cms-h2" style={{ marginBottom: "1rem" }}>Nuevo usuario</h2>
      <form onSubmit={handleSubmit} style={{ maxWidth: 400 }}>
        <div className="cms-form-group">
          <label className="cms-label" htmlFor="new-email">Email</label>
          <input
            id="new-email" type="email" className="cms-input"
            value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
        </div>
        <div className="cms-form-group">
          <label className="cms-label" htmlFor="new-pass">Contraseña</label>
          <input
            id="new-pass" type="password" className="cms-input"
            value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
            required minLength={8}
          />
        </div>
        <div className="cms-form-group">
          <label className="cms-label" htmlFor="new-rol">Rol</label>
          <select
            id="new-rol" className="cms-select"
            value={form.rol} onChange={(e) => setForm({ ...form, rol: e.target.value as "admin" | "editor" })}
          >
            <option value="editor">Editor</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        {error && <p className="cms-error">{error}</p>}
        <button type="submit" className="cms-btn cms-btn-primary">
          Crear usuario
        </button>
      </form>
    </>
  );
}
