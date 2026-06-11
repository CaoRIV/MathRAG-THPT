import { AlertTriangle, WifiOff } from "lucide-react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";
import type { ChatMode, ChatResponse } from "../types/generated/api";
import { AssistantAnswer } from "../components/chat/AssistantAnswer";
import { ChatComposer } from "../components/chat/ChatComposer";
import { EmptyChat } from "../components/chat/EmptyChat";
import { ModeSwitch } from "../components/chat/ModeSwitch";
import { RetrievalStatus } from "../components/chat/RetrievalStatus";

interface Exchange {
  question: string;
  response: ChatResponse;
}

export function ChatPage() {
  const [mode, setMode] = useState<ChatMode>("study");
  const [conversationId, setConversationId] = useState<string>();
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const readiness = useQuery({
    queryKey: ["readiness"],
    queryFn: api.readiness,
    refetchInterval: 30_000,
  });
  const mutation = useMutation({
    mutationFn: api.chat,
    onSuccess: (response, request) => {
      setConversationId(response.conversation_id);
      setExchanges((items) => [...items, { question: request.message, response }]);
    },
  });

  function ask(message: string) {
    mutation.mutate({
      message,
      mode,
      conversation_id: conversationId,
      assistance_level: mode === "exam" ? "hint" : null,
      filters: { grade: 12 },
    });
  }

  const ollamaUnavailable =
    readiness.data?.checks.ollama?.status === "degraded";

  return (
    <div className="grid min-h-[calc(100vh-7rem)] gap-6 xl:grid-cols-[minmax(0,1fr)_300px]">
      <section className="flex min-w-0 flex-col">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary-600">
              Trợ lý có dẫn nguồn
            </p>
            <h1 className="mt-1 font-heading text-2xl font-semibold text-ink">
              Không gian học Toán
            </h1>
          </div>
          <ModeSwitch value={mode} onChange={setMode} />
        </header>

        {ollamaUnavailable && (
          <div className="mt-5 flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            <p>
              Ollama chưa sẵn sàng. Hệ thống vẫn trả lời bằng nội dung truy xuất trực tiếp.
            </p>
          </div>
        )}

        <div className="flex-1">
          {exchanges.length === 0 && !mutation.isPending ? (
            <EmptyChat onPrompt={ask} />
          ) : (
            <div className="space-y-6 py-6" aria-live="polite">
              {exchanges.map((exchange, index) => (
                <div key={`${exchange.response.conversation_id}-${index}`} className="space-y-3">
                  <div className="ml-auto max-w-2xl rounded-2xl rounded-br-md bg-ink px-5 py-3.5 text-sm leading-6 text-white">
                    {exchange.question}
                  </div>
                  <AssistantAnswer response={exchange.response} />
                </div>
              ))}
              {mutation.isPending && <RetrievalStatus />}
              {mutation.isError && (
                <div
                  className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-900"
                  role="alert"
                >
                  <WifiOff className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
                  <div>
                    <p className="font-semibold">Không thể nhận câu trả lời</p>
                    <p className="mt-1 text-red-800">{mutation.error.message}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="sticky bottom-3 z-10 mt-auto pt-3">
          <ChatComposer mode={mode} disabled={mutation.isPending} onSubmit={ask} />
        </div>
      </section>

      <aside className="hidden space-y-4 xl:block">
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-card">
          <h2 className="font-heading text-base font-semibold text-ink">
            Cách MathRAG hỗ trợ
          </h2>
          <ol className="mt-4 space-y-4">
            {[
              ["01", "Hiểu câu hỏi và nhận diện chủ đề"],
              ["02", "Tìm theo từ khóa, ngữ nghĩa và công thức"],
              ["03", "Trả lời kèm nguồn để bạn kiểm chứng"],
            ].map(([number, label]) => (
              <li key={number} className="flex gap-3 text-sm leading-5 text-muted">
                <span className="font-heading text-xs font-bold text-primary-600">{number}</span>
                {label}
              </li>
            ))}
          </ol>
        </div>
        <div className="rounded-3xl border border-cyan-100 bg-cyan-50/70 p-5">
          <h2 className="text-sm font-semibold text-cyan-950">Mẹo nhập công thức</h2>
          <p className="mt-2 text-xs leading-5 text-cyan-900">
            Dùng LaTeX giữa hai dấu <code className="rounded bg-white px-1">$</code>, ví dụ{" "}
            <code className="rounded bg-white px-1">$\int x^2 dx$</code>.
          </p>
        </div>
      </aside>
    </div>
  );
}

