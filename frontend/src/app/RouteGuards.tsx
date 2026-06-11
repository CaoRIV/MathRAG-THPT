import { Navigate, Outlet, useLocation } from "react-router-dom";
import { LoadingDots } from "../components/ui/LoadingDots";
import { useAuth } from "./AuthProvider";

export function ProtectedRoute() {
  const { user, isLoading } = useAuth();
  const location = useLocation();
  if (isLoading) {
    return (
      <div className="grid min-h-screen place-items-center bg-canvas">
        <LoadingDots label="Đang kiểm tra phiên đăng nhập" />
      </div>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return <Outlet />;
}

export function AdminRoute() {
  const { user } = useAuth();
  if (user?.role !== "admin") return <Navigate to="/chat" replace />;
  return <Outlet />;
}

export function GuestRoute() {
  const { user, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="grid min-h-screen place-items-center bg-canvas">
        <LoadingDots label="Đang tải" />
      </div>
    );
  }
  return user ? <Navigate to={user.role === "admin" ? "/admin/documents" : "/chat"} replace /> : <Outlet />;
}
