import { ArrowUpRight, BookOpenText } from "lucide-react";
import { Link } from "react-router-dom";
import type { RelatedDocument } from "../../types/generated/api";
import { Badge } from "../ui/Badge";
import { contentLabels } from "../../lib/utils";

export function SourceCard({ document }: { document: RelatedDocument }) {
  return (
    <Link
      to={`/documents/${document.id}`}
      className="group block cursor-pointer rounded-2xl border border-slate-200 bg-white p-4 transition-colors duration-200 hover:border-primary-200 hover:bg-primary-50/40 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100"
    >
      <div className="flex items-start justify-between gap-3">
        <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-primary-50 text-primary-600">
          <BookOpenText className="h-4 w-4" aria-hidden="true" />
        </span>
        <ArrowUpRight
          className="h-4 w-4 text-slate-400 transition-colors group-hover:text-primary-600"
          aria-hidden="true"
        />
      </div>
      <h3 className="mt-3 line-clamp-2 text-sm font-semibold leading-5 text-ink">
        {document.title}
      </h3>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <Badge tone="slate">{contentLabels[document.content_type] ?? document.content_type}</Badge>
        <span className="text-xs text-muted">{document.topic}</span>
      </div>
    </Link>
  );
}

