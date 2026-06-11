import { DatabaseZap, SearchCheck } from "lucide-react";
import { LoadingDots } from "../ui/LoadingDots";

export function RetrievalStatus() {
  return (
    <div
      className="rounded-2xl border border-primary-100 bg-primary-50/60 p-4"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center gap-3">
        <span className="grid h-9 w-9 place-items-center rounded-xl bg-white text-primary-600 shadow-sm">
          <DatabaseZap className="h-4 w-4" aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-ink">Đang tìm căn cứ phù hợp</p>
          <p className="mt-0.5 flex items-center gap-2 text-xs text-muted">
            <SearchCheck className="h-3.5 w-3.5" aria-hidden="true" />
            BM25, ngữ nghĩa và công thức
          </p>
        </div>
        <LoadingDots />
      </div>
    </div>
  );
}
