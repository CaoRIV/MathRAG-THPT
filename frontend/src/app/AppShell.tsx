import {
  BookOpen,
  Bot,
  FileQuestion,
  LogOut,
  Menu,
  Search,
  ShieldCheck,
  UserRound,
  X,
} from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { BrandMark } from "../components/brand/BrandMark";
import { cn } from "../lib/utils";
import { useAuth } from "./AuthProvider";

const navigation = [
  { to: "/chat", label: "Trợ lý học tập", icon: Bot },
  { to: "/search", label: "Tìm tài liệu", icon: Search },
  { to: "/topics", label: "Chủ đề Toán 12", icon: BookOpen },
  { to: "/practice", label: "Luyện tập", icon: FileQuestion },
];

function Navigation({ onNavigate }: { onNavigate?: () => void }) {
  const { user } = useAuth();
  const items = user?.role === "admin"
    ? [
        ...navigation,
        { to: "/admin/documents", label: "Quản trị tài liệu", icon: ShieldCheck },
      ]
    : navigation;
  return (
    <nav aria-label="Điều hướng chính" className="space-y-1">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              "flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100",
              isActive
                ? "bg-primary-50 text-primary-700"
                : "text-muted hover:bg-slate-50 hover:text-ink",
            )
          }
        >
          <item.icon className="h-[18px] w-[18px]" aria-hidden="true" />
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}

export function AppShell() {
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  return (
    <div className="min-h-screen bg-canvas text-ink">
      <a
        href="#main-content"
        className="fixed left-4 top-3 z-[70] -translate-y-20 rounded-lg bg-ink px-4 py-2 text-sm font-semibold text-white transition-transform focus:translate-y-0"
      >
        Bỏ qua điều hướng
      </a>
      <header className="fixed inset-x-3 top-3 z-30 flex h-16 items-center justify-between rounded-2xl border border-white/80 bg-white/90 px-4 shadow-card backdrop-blur-xl lg:hidden">
        <NavLink to="/chat" className="flex items-center gap-2">
          <BrandMark size="sm" />
          <span className="font-heading text-sm font-bold">MathRAG THPT</span>
        </NavLink>
        <button
          onClick={() => setMobileOpen((value) => !value)}
          className="grid h-10 w-10 cursor-pointer place-items-center rounded-xl text-muted transition-colors hover:bg-slate-50 hover:text-ink focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100"
          aria-label={mobileOpen ? "Đóng menu" : "Mở menu"}
          aria-expanded={mobileOpen}
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </header>

      {mobileOpen && (
        <div className="fixed inset-x-3 top-20 z-30 rounded-2xl border border-slate-200 bg-white p-3 shadow-soft lg:hidden">
          <Navigation onNavigate={() => setMobileOpen(false)} />
          <div className="mt-3 border-t border-slate-100 pt-3">
            <div className="flex items-center gap-3 px-3 py-2">
              <span className="grid h-9 w-9 place-items-center rounded-xl bg-primary-50 text-primary-700">
                <UserRound className="h-4 w-4" aria-hidden="true" />
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-ink">{user?.full_name}</p>
                <p className="truncate text-xs text-muted">{user?.email}</p>
              </div>
              <button onClick={logout} aria-label="Đăng xuất" className="grid h-9 w-9 cursor-pointer place-items-center rounded-xl text-muted hover:bg-red-50 hover:text-red-700 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-red-100">
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      <aside className="fixed inset-y-4 left-4 z-20 hidden w-64 flex-col rounded-3xl border border-white bg-white/90 p-4 shadow-soft backdrop-blur-xl lg:flex">
        <NavLink to="/chat" className="flex items-center gap-3 rounded-2xl px-2 py-2">
          <BrandMark size="md" />
          <span>
            <span className="block font-heading text-base font-bold text-ink">MathRAG</span>
            <span className="block text-[11px] font-medium uppercase tracking-[0.18em] text-muted">
              THPT
            </span>
          </span>
        </NavLink>
        <div className="mt-6">
          <Navigation />
        </div>
        <div className="mt-auto rounded-2xl border border-slate-200 bg-slate-50/80 p-3">
          <div className="flex items-center gap-3">
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-primary-100 text-primary-700">
              <UserRound className="h-4 w-4" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-ink">{user?.full_name}</p>
              <p className="mt-0.5 text-[11px] font-medium uppercase tracking-wider text-primary-700">
                {user?.role === "admin" ? "Quản trị viên" : "Học sinh"}
              </p>
            </div>
            <button onClick={logout} aria-label="Đăng xuất" title="Đăng xuất" className="grid h-9 w-9 cursor-pointer place-items-center rounded-xl text-muted transition-colors hover:bg-red-50 hover:text-red-700 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-red-100">
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      <main id="main-content" className="px-3 pb-8 pt-22 lg:ml-72 lg:px-8 lg:pt-8">
        <div className="mx-auto max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
