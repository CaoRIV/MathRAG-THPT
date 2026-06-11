import { Eye, EyeOff, LockKeyhole, LogIn, Mail } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../app/AuthProvider";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const user = await login(email, password);
      const requestedPath = location.state?.from;
      navigate(
        requestedPath ?? (user.role === "admin" ? "/admin/documents" : "/chat"),
        { replace: true },
      );
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Đăng nhập thất bại.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <>
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary-600">
        Chào mừng trở lại
      </p>
      <h1 className="mt-2 font-heading text-3xl font-semibold text-ink">Đăng nhập</h1>
      <p className="mt-2 text-sm leading-6 text-muted">
        Tiếp tục phiên học và truy cập kho tài liệu MathRAG.
      </p>
      <form onSubmit={submit} className="mt-7 space-y-5">
        <label className="block text-sm font-semibold text-ink" htmlFor="login-email">
          Email
          <span className="relative mt-2 block">
            <Mail className="pointer-events-none absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" aria-hidden="true" />
            <input id="login-email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} placeholder="ban@example.com" className="w-full rounded-xl border border-slate-200 py-3 pl-10 pr-4 font-normal text-ink transition-colors placeholder:text-slate-400 focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100" />
          </span>
        </label>
        <label className="block text-sm font-semibold text-ink" htmlFor="login-password">
          Mật khẩu
          <span className="relative mt-2 block">
            <LockKeyhole className="pointer-events-none absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" aria-hidden="true" />
            <input id="login-password" type={showPassword ? "text" : "password"} autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} className="w-full rounded-xl border border-slate-200 py-3 pl-10 pr-11 font-normal text-ink transition-colors focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100" />
            <button type="button" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"} className="absolute right-2 top-2 grid h-9 w-9 cursor-pointer place-items-center rounded-lg text-muted hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100">
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </span>
        </label>
        {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>}
        <button disabled={isSubmitting} className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-xl bg-primary-600 px-5 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-primary-700 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100 disabled:cursor-wait disabled:bg-primary-400">
          <LogIn className="h-4 w-4" aria-hidden="true" />
          {isSubmitting ? "Đang đăng nhập..." : "Đăng nhập"}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-muted">
        Chưa có tài khoản?{" "}
        <Link to="/register" className="font-semibold text-primary-700 hover:text-primary-800">
          Đăng ký miễn phí
        </Link>
      </p>
    </>
  );
}
