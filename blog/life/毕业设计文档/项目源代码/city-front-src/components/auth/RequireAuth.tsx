import { Navigate, useLocation } from "react-router-dom";
import {JSX} from "react";

type RequireAuthProps = {
  children: JSX.Element;
};

export function RequireAuth({ children }: RequireAuthProps) {
  const location = useLocation();
  const token = window.localStorage.getItem("auth_token");

  if (!token) {
    return <Navigate to="/auth/login" state={{ from: location.pathname }} replace />;
  }

  return children;
}
