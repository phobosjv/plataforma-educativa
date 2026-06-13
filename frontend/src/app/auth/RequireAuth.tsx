import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";

interface Props {
  children: React.ReactNode;
  rol?: "admin" | "editor";
}

export function RequireAuth({ children, rol }: Props) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (rol === "admin" && user.rol !== "admin") {
    return <Navigate to="/admin" replace />;
  }

  return <>{children}</>;
}
