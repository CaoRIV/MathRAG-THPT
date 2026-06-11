import { AlertCircle, CheckCircle2, Library } from "lucide-react";
import type { ChatResponse } from "../../types/generated/api";
import { ChatbotAvatar } from "../brand/BrandMark";
import { MathContent } from "../math/MathContent";
import { EvidenceDrawer } from "../sources/EvidenceDrawer";
import { SourceCard } from "../sources/SourceCard";

export function AssistantAnswer({ response }: { response: ChatResponse }) {
  const isFallback = Boolean(response.fallback_status);
  return (
    <article className="rounded-3xl border border-slate-200 bg-white shadow-card">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-5 py-4 sm:px-6">
        <div className="flex items-center gap-3">
          <ChatbotAvatar />
          <div>
            <h2 className="text-sm font-semibold text-ink">MathRAG trả lời</h2>
            <p className="mt-0.5 flex items-center gap-1.5 text-xs text-muted">
              {isFallback ? (
                <AlertCircle className="h-3.5 w-3.5 text-amber-600" aria-hidden="true" />
              ) : (
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" aria-hidden="true" />
              )}
              {isFallback ? "Đang dùng câu trả lời dự phòng có căn cứ" : "Đã đối chiếu nguồn"}
            </p>
          </div>
        </div>
        <EvidenceDrawer evidence={response.evidence} />
      </header>
      <div className="px-5 py-6 sm:px-7">
        {response.fallback_status === "insufficient_evidence" && (
          <div className="mb-5 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            Kho tài liệu hiện chưa đủ bằng chứng để trả lời chắc chắn.
          </div>
        )}
        <MathContent>{response.answer}</MathContent>
        {response.citations.length > 0 && (
          <section className="mt-7 border-t border-slate-100 pt-5">
            <div className="flex items-center gap-2 text-sm font-semibold text-ink">
              <Library className="h-4 w-4 text-primary-600" aria-hidden="true" />
              Nguồn đã sử dụng
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {response.citations.map((citation) => (
                <a
                  key={citation.id}
                  href={citation.source_url ?? `/documents/${citation.document_id}`}
                  target={citation.source_url ? "_blank" : undefined}
                  rel={citation.source_url ? "noreferrer" : undefined}
                  className="cursor-pointer rounded-xl bg-slate-50 px-3 py-2 text-xs font-medium text-slate-700 ring-1 ring-inset ring-slate-200 transition-colors hover:bg-primary-50 hover:text-primary-700 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100"
                >
                  {citation.label} {citation.title}
                </a>
              ))}
            </div>
          </section>
        )}
      </div>
      {response.related_documents.length > 0 && (
        <section className="border-t border-slate-100 bg-slate-50/50 px-5 py-5 sm:px-7">
          <h3 className="text-sm font-semibold text-ink">Tài liệu nên xem tiếp</h3>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {response.related_documents.slice(0, 4).map((document) => (
              <SourceCard key={document.id} document={document} />
            ))}
          </div>
        </section>
      )}
    </article>
  );
}
