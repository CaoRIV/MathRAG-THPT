import { ArrowLeft, BookMarked, Search } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { Link, useLocation, useParams } from "react-router-dom";
import { api } from "../lib/api";
import type { TopicItem } from "../types/generated/api";
import { Badge } from "../components/ui/Badge";
import { contentLabels } from "../lib/utils";

export function TopicDetailPage() {
  const { slug } = useParams();
  const location = useLocation();
  const topic = location.state?.topic as TopicItem | undefined;
  const name = topic?.name ?? slug?.replaceAll("-", " ") ?? "Chủ đề";
  const search = useMutation({
    mutationFn: () => api.search(name),
  });

  return (
    <div className="mx-auto max-w-5xl">
      <Link to="/topics" className="inline-flex items-center gap-2 text-sm font-semibold text-primary-700 hover:text-primary-800">
        <ArrowLeft className="h-4 w-4" aria-hidden="true" /> Tất cả chủ đề
      </Link>
      <header className="mt-6 rounded-3xl bg-gradient-to-br from-primary-700 to-primary-500 p-7 text-white shadow-soft sm:p-10">
        <BookMarked className="h-8 w-8 text-primary-100" aria-hidden="true" />
        <h1 className="mt-5 font-heading text-3xl font-semibold capitalize">{name}</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-primary-50">
          {topic?.description ?? "Tổng hợp lý thuyết, công thức và bài luyện theo chủ đề."}
        </p>
        <button
          onClick={() => search.mutate()}
          className="mt-6 inline-flex cursor-pointer items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-primary-700 transition-colors hover:bg-primary-50 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-white/30"
        >
          <Search className="h-4 w-4" aria-hidden="true" /> Xem tài liệu
        </button>
      </header>
      <div className="mt-6 space-y-3">
        {search.data?.items.map((item) => (
          <Link key={item.chunk_id} to={`/documents/${item.document_id}`} className="block rounded-2xl border border-slate-200 bg-white p-5 transition-colors hover:border-primary-200">
            <div className="flex gap-2"><Badge>{contentLabels[item.content_type] ?? item.content_type}</Badge></div>
            <h2 className="mt-3 font-heading text-lg font-semibold text-ink">{item.title}</h2>
            <p className="mt-2 text-sm leading-6 text-muted">{item.excerpt}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

