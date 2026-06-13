import {
  createContext,
  useCallback,
  useContext,
  useState,
} from "react";
import { api } from "../../shared/api/client";

type Rol = "admin" | "editor";

interface AuthUser {
  id: string;
  rol: Rol;
}

interface AuthState {
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function parseToken(token: string): AuthUser | null {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return { id: payload.sub as string, rol: payload.rol as Rol };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const token = localStorage.getItem("auth_token");
    return {
      token,
      user: token ? parseToken(token) : null,
      isLoading: false,
    };
  });

  const login = useCallback(async (email: string, password: string) => {
    setState((s) => ({ ...s, isLoading: true }));

    const { data, error } = await api.POST("/api/v1/auth/token", {
      body: { username: email, password, scope: "" },
      bodySerializer: (body) =>
        new URLSearchParams(body as Record<string, string>),
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    if (error || !data) {
      setState((s) => ({ ...s, isLoading: false }));
      throw new Error("Credenciales incorrectas");
    }

    const token = data.access_token;
    localStorage.setItem("auth_token", token);
    setState({ token, user: parseToken(token), isLoading: false });
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("auth_token");
    setState({ token: null, user: null, isLoading: false });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}
