import { ArrowLeft, ExternalLink, FileText } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";
import { MathContent } from "../components/math/MathContent";
import { Badge } from "../components/ui/Badge";
import { LoadingDots } from "../components/ui/LoadingDots";
import { contentLabels } from "../lib/utils";

export function DocumentPage() {
  const { id = "" } = useParams();
  const document = useQuery({
    queryKey: ["document", id],
    queryFn: () => api.document(id),
    enabled: Boolean(id),
  });
  if (document.isLoading) return <LoadingDots label="Đang tải tài liệu" />;
  if (!document.data) return <p className="text-sm text-muted">Không tìm thấy tài liệu.</p>;
  return (
    <article className="mx-auto max-w-4xl">
      <Link to="/search" className="inline-flex items-center gap-2 text-sm font-semibold text-primary-700">
        <ArrowLeft className="h-4 w-4" aria-hidden="true" /> Quay lại tìm kiếm
      </Link>
      <header className="mt-6 rounded-3xl border border-slate-200 bg-white p-7 shadow-card sm:p-9">
        <div className="flex flex-wrap items-center gap-2">
          <Badge>{contentLabels[document.data.content_type] ?? document.data.content_type}</Badge>
          <Badge tone="slate">Toán {document.data.grade}</Badge>
          <span className="text-xs text-muted">{document.data.topic}</span>
        </div>
        <h1 className="mt-5 font-heading text-3xl font-semibold leading-tight text-ink">{document.data.title}</h1>
        <p className="mt-3 text-sm leading-6 text-muted">{document.data.description}</p>
        {document.data.source_url && (
          <a href={document.data.source_url} target="_blank" rel="noreferrer" className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-primary-700 hover:text-primary-800">
            Mở nguồn gốc <ExternalLink className="h-4 w-4" aria-hidden="true" />
          </a>
        )}
      </header>
      <div className="mt-5 space-y-4">
        {document.data.sections.map((section) => (
          <section key={section.id} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card sm:p-8">
            <div className="flex items-center gap-2 text-primary-600">
              <FileText className="h-4 w-4" aria-hidden="true" />
              <span className="text-xs font-semibold uppercase tracking-wider">
                {contentLabels[section.content_type] ?? section.content_type}
              </span>
            </div>
            {section.heading && <h2 className="mt-3 font-heading text-xl font-semibold text-ink">{section.heading}</h2>}
            <div className="mt-4"><MathContent>{section.content}</MathContent></div>
          </section>
        ))}
      </div>
    </article>
  );
}

