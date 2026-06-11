import { ArrowRight, BookOpen, Sigma } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { cn } from "../lib/utils";
import { LoadingDots } from "../components/ui/LoadingDots";

const accentClasses: Record<string, string> = {
  violet: "bg-violet-50 text-violet-700",
  cyan: "bg-cyan-50 text-cyan-700",
  amber: "bg-amber-50 text-amber-700",
  emerald: "bg-emerald-50 text-emerald-700",
  rose: "bg-rose-50 text-rose-700",
};

export function TopicsPage() {
  const topics = useQuery({ queryKey: ["topics"], queryFn: api.topics });
  return (
    <div className="mx-auto max-w-6xl">
      <header className="flex flex-wrap items-end justify-between gap-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary-600">Lộ trình Toán 12</p>
          <h1 className="mt-2 font-heading text-3xl font-semibold text-ink">Ôn tập theo chủ đề</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">
            Đi từ nền tảng đến bài thi. Mỗi chủ đề kết nối lý thuyết, công thức và bài luyện liên quan.
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-xl bg-white px-3 py-2 text-xs font-semibold text-muted ring-1 ring-slate-200">
          <BookOpen className="h-4 w-4 text-primary-600" aria-hidden="true" />
          Toán 12 + Ôn thi THPT
        </div>
      </header>
      {topics.isLoading && <div className="mt-8"><LoadingDots /></div>}
      <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {topics.data?.map((topic) => (
          <Link
            key={topic.slug}
            to={`/topics/${topic.slug}`}
            state={{ topic }}
            className="group cursor-pointer rounded-3xl border border-slate-200 bg-white p-6 shadow-card transition-colors hover:border-primary-200 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100"
          >
            <span className={cn("grid h-11 w-11 place-items-center rounded-2xl", accentClasses[topic.accent] ?? accentClasses.violet)}>
              <Sigma className="h-5 w-5" aria-hidden="true" />
            </span>
            <h2 className="mt-5 font-heading text-xl font-semibold text-ink">{topic.name}</h2>
            <p className="mt-2 min-h-12 text-sm leading-6 text-muted">{topic.description}</p>
            <div className="mt-5 flex items-center justify-between border-t border-slate-100 pt-4">
              <span className="text-xs font-medium text-muted">{topic.document_count} tài liệu</span>
              <ArrowRight className="h-4 w-4 text-primary-600 transition-transform group-hover:translate-x-1" aria-hidden="true" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

