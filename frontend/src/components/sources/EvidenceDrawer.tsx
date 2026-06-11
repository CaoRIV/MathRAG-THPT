import * as Dialog from "@radix-ui/react-dialog";
import { BarChart3, X } from "lucide-react";
import type { Evidence } from "../../types/generated/api";
import { Badge } from "../ui/Badge";
import { contentLabels } from "../../lib/utils";

export function EvidenceDrawer({ evidence }: { evidence: Evidence[] }) {
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>
        <button className="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-ink transition-colors hover:border-primary-200 hover:bg-primary-50 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100">
          <BarChart3 className="h-4 w-4 text-primary-600" aria-hidden="true" />
          Xem cách truy xuất
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-ink/20 backdrop-blur-sm" />
        <Dialog.Content className="fixed inset-y-0 right-0 z-50 w-full max-w-lg overflow-y-auto border-l border-slate-200 bg-canvas p-5 shadow-2xl focus:outline-none sm:p-7">
          <div className="flex items-start justify-between gap-4">
            <div>
              <Dialog.Title className="font-heading text-xl font-semibold text-ink">
                Minh bạch truy xuất
              </Dialog.Title>
              <Dialog.Description className="mt-1 text-sm leading-6 text-muted">
                Các đoạn tài liệu được xếp hạng trước khi tạo câu trả lời.
              </Dialog.Description>
            </div>
            <Dialog.Close className="grid h-10 w-10 cursor-pointer place-items-center rounded-xl border border-slate-200 bg-white text-muted transition-colors hover:text-ink focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100">
              <X className="h-5 w-5" aria-hidden="true" />
              <span className="sr-only">Đóng</span>
            </Dialog.Close>
          </div>
          <div className="mt-6 space-y-4">
            {evidence.map((item, index) => (
              <article key={item.chunk_id} className="rounded-2xl border border-slate-200 bg-white p-5">
                <div className="flex items-center justify-between gap-3">
                  <Badge>{`Nguồn ${index + 1}`}</Badge>
                  <span className="text-xs font-semibold text-primary-700">
                    {Math.round(item.score * 100)}% phù hợp
                  </span>
                </div>
                <h3 className="mt-3 font-heading text-base font-semibold text-ink">{item.title}</h3>
                <p className="mt-2 text-sm leading-6 text-muted">{item.excerpt}</p>
                <div className="mt-4 flex flex-wrap gap-2 text-[11px] text-slate-500">
                  <span>{item.topic}</span>
                  <span aria-hidden="true">•</span>
                  <span>{contentLabels[item.content_type] ?? item.content_type}</span>
                </div>
              </article>
            ))}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

