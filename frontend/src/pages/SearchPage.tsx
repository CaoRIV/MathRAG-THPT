import { Search, SlidersHorizontal } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Badge } from "../components/ui/Badge";
import { LoadingDots } from "../components/ui/LoadingDots";
import { contentLabels } from "../lib/utils";

export function SearchPage() {
  const [query, setQuery] = useState("");
  const mutation = useMutation({
    mutationFn: (value: string) => api.search(value),
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    if (query.trim()) mutation.mutate(query.trim());
  }

  return (
    <div className="mx-auto max-w-5xl">
      <header>
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary-600">
          Kho học liệu
        </p>
        <h1 className="mt-2 font-heading text-3xl font-semibold text-ink">Tìm đúng tài liệu cần học</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">
          Tìm theo chủ đề, câu hỏi hoặc công thức. Kết quả kết hợp từ khóa, ngữ nghĩa và cấu trúc toán.
        </p>
      </header>
      <form onSubmit={submit} className="mt-7 flex gap-3 rounded-2xl border border-slate-200 bg-white p-2 shadow-card">
        <label htmlFor="search-library" className="sr-only">Tìm trong kho tài liệu</label>
        <Search className="ml-3 mt-3 h-5 w-5 shrink-0 text-slate-400" aria-hidden="true" />
        <input
          id="search-library"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Ví dụ: công thức khoảng cách từ điểm đến mặt phẳng"
          className="min-w-0 flex-1 bg-transparent px-1 py-2.5 text-sm text-ink placeholder:text-slate-400 focus:outline-none"
        />
        <button className="inline-flex cursor-pointer items-center gap-2 rounded-xl bg-primary-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-700 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100">
          <SlidersHorizontal className="h-4 w-4" aria-hidden="true" />
          Tìm kiếm
        </button>
      </form>

      <div className="mt-8" aria-live="polite">
        {mutation.isPending && (
          <div className="flex items-center gap-3 rounded-2xl border border-primary-100 bg-primary-50 p-4 text-sm font-medium text-primary-800">
            <LoadingDots />
            Đang xếp hạng tài liệu...
          </div>
        )}
        {mutation.data?.items.length === 0 && (
          <div className="rounded-3xl border border-slate-200 bg-white p-10 text-center">
            <h2 className="font-heading text-xl font-semibold text-ink">Chưa tìm thấy kết quả phù hợp</h2>
            <p className="mt-2 text-sm text-muted">Hãy thử tên chủ đề rộng hơn hoặc nhập biểu thức LaTeX.</p>
          </div>
        )}
        {mutation.data && mutation.data.items.length > 0 && (
          <>
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-muted">
                Tìm thấy <strong className="text-ink">{mutation.data.total}</strong> đoạn phù hợp
              </p>
            </div>
            <div className="space-y-3">
              {mutation.data.items.map((item) => (
                <Link
                  key={item.chunk_id}
                  to={`/documents/${item.document_id}`}
                  className="block cursor-pointer rounded-2xl border border-slate-200 bg-white p-5 shadow-card transition-colors hover:border-primary-200 hover:bg-primary-50/30 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100"
                >
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <Badge>{contentLabels[item.content_type] ?? item.content_type}</Badge>
                      <span className="text-xs text-muted">{item.topic}</span>
                    </div>
                    <span className="text-xs font-semibold text-primary-700">
                      {Math.round(item.score * 100)}% phù hợp
                    </span>
                  </div>
                  <h2 className="mt-3 font-heading text-lg font-semibold text-ink">{item.title}</h2>
                  <p className="mt-2 text-sm leading-6 text-muted">{item.excerpt}</p>
                </Link>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

