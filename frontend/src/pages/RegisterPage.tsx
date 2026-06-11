import { Eye, EyeOff, LockKeyhole, Mail, UserRound, UserRoundPlus } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../app/AuthProvider";

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (password !== confirmPassword) {
      setError("Mật khẩu xác nhận chưa khớp.");
      return;
    }
    setIsSubmitting(true);
    try {
      await register(fullName, email, password);
      navigate("/chat", { replace: true });
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Đăng ký thất bại.");
    } finally {
      setIsSubmitting(false);
    }
  }

  const inputClass = "w-full rounded-xl border border-slate-200 py-3 pl-10 pr-4 font-normal text-ink transition-colors placeholder:text-slate-400 focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100";
  return (
    <>
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary-600">
        Bắt đầu học cùng MathRAG
      </p>
      <h1 className="mt-2 font-heading text-3xl font-semibold text-ink">Tạo tài khoản</h1>
      <p className="mt-2 text-sm leading-6 text-muted">
        Tài khoản mới được cấp quyền người dùng và truy cập đầy đủ chức năng học tập.
      </p>
      <form onSubmit={submit} className="mt-7 space-y-4">
        <label className="block text-sm font-semibold text-ink" htmlFor="register-name">
          Họ và tên
          <span className="relative mt-2 block">
            <UserRound className="pointer-events-none absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
            <input id="register-name" required minLength={2} value={fullName} onChange={(event) => setFullName(event.target.value)} className={inputClass} placeholder="Nguyễn Văn An" />
          </span>
        </label>
        <label className="block text-sm font-semibold text-ink" htmlFor="register-email">
          Email
          <span className="relative mt-2 block">
            <Mail className="pointer-events-none absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
            <input id="register-email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} className={inputClass} placeholder="ban@example.com" />
          </span>
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block text-sm font-semibold text-ink" htmlFor="register-password">
            Mật khẩu
            <span className="relative mt-2 block">
              <LockKeyhole className="pointer-events-none absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
              <input id="register-password" type={showPassword ? "text" : "password"} autoComplete="new-password" required minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} className={`${inputClass} pr-11`} />
              <button type="button" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"} className="absolute right-2 top-2 grid h-9 w-9 cursor-pointer place-items-center rounded-lg text-muted hover:bg-slate-50">
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </span>
          </label>
          <label className="block text-sm font-semibold text-ink" htmlFor="confirm-password">
            Xác nhận
            <span className="relative mt-2 block">
              <LockKeyhole className="pointer-events-none absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
              <input id="confirm-password" type={showPassword ? "text" : "password"} autoComplete="new-password" required value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} className={inputClass} />
            </span>
          </label>
        </div>
        <p className="text-xs leading-5 text-muted">Tối thiểu 8 ký tự. Không sử dụng lại mật khẩu quan trọng ở dịch vụ khác.</p>
        {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>}
        <button disabled={isSubmitting} className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-xl bg-primary-600 px-5 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-primary-700 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100 disabled:cursor-wait disabled:bg-primary-400">
          <UserRoundPlus className="h-4 w-4" aria-hidden="true" />
          {isSubmitting ? "Đang tạo tài khoản..." : "Tạo tài khoản"}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-muted">
        Đã có tài khoản?{" "}
        <Link to="/login" className="font-semibold text-primary-700 hover:text-primary-800">Đăng nhập</Link>
      </p>
    </>
  );
}
