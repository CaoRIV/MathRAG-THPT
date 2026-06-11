import { BookOpenCheck, FileSearch, ShieldCheck } from "lucide-react";
import { Outlet } from "react-router-dom";
import { BrandMark } from "../brand/BrandMark";

export function AuthLayout() {
  return (
    <main className="min-h-screen bg-canvas p-3 sm:p-6">
      <div className="mx-auto grid min-h-[calc(100vh-1.5rem)] max-w-6xl overflow-hidden rounded-3xl border border-white bg-white shadow-soft sm:min-h-[calc(100vh-3rem)] lg:grid-cols-[1.05fr_0.95fr]">
        <section className="relative hidden overflow-hidden bg-gradient-to-br from-[#21164f] via-primary-700 to-accent-600 p-10 text-white lg:flex lg:flex-col">
          <div className="absolute -right-28 -top-28 h-80 w-80 rounded-full bg-white/10 blur-2xl" />
          <div className="absolute -bottom-32 -left-28 h-96 w-96 rounded-full bg-cyan-300/10 blur-3xl" />
          <div className="relative flex items-center gap-3">
            <BrandMark size="md" />
            <div>
              <p className="font-heading text-lg font-bold">MathRAG THPT</p>
              <p className="text-xs text-primary-100">Học Toán với căn cứ rõ ràng</p>
            </div>
          </div>
          <div className="relative my-auto max-w-lg">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-200">
              Không gian học tập cá nhân
            </p>
            <h1 className="mt-4 font-heading text-4xl font-semibold leading-tight">
              Học đúng trọng tâm, kiểm chứng từng nguồn.
            </h1>
            <p className="mt-5 text-sm leading-7 text-primary-100">
              Đăng nhập để sử dụng trợ lý Toán 12, tìm tài liệu và luyện thi THPT
              trong một trải nghiệm tập trung.
            </p>
            <div className="mt-9 grid gap-3">
              {[
                [BookOpenCheck, "Giải thích lý thuyết và công thức có dẫn nguồn"],
                [FileSearch, "Tìm ví dụ và tài liệu tương tự theo ngữ nghĩa"],
                [ShieldCheck, "Phân quyền rõ ràng, kho tài liệu được quản trị"],
              ].map(([Icon, label]) => (
                <div key={label as string} className="flex items-center gap-3 text-sm text-white">
                  <span className="grid h-9 w-9 place-items-center rounded-xl bg-white/10">
                    <Icon className="h-4 w-4" aria-hidden="true" />
                  </span>
                  {label as string}
                </div>
              ))}
            </div>
          </div>
          <p className="relative text-xs text-primary-200">
            Dành cho học sinh và quản trị viên kho học liệu.
          </p>
        </section>
        <section className="grid place-items-center p-6 sm:p-10">
          <div className="w-full max-w-md">
            <div className="mb-8 flex items-center gap-3 lg:hidden">
              <BrandMark size="md" />
              <div>
                <p className="font-heading font-bold text-ink">MathRAG THPT</p>
                <p className="text-xs text-muted">Trợ lý học Toán có dẫn nguồn</p>
              </div>
            </div>
            <Outlet />
          </div>
        </section>
      </div>
    </main>
  );
}
