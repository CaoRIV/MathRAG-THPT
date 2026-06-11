import { CornerDownLeft, Lightbulb, Send } from "lucide-react";
import { useState, type FormEvent, type KeyboardEvent } from "react";
import type { ChatMode } from "../../types/generated/api";

export function ChatComposer({
  mode,
  disabled,
  onSubmit,
}: {
  mode: ChatMode;
  disabled: boolean;
  onSubmit: (message: string) => void;
}) {
  const [message, setMessage] = useState("");

  function submit(event?: FormEvent) {
    event?.preventDefault();
    const value = message.trim();
    if (!value || disabled) return;
    onSubmit(value);
    setMessage("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  }

  return (
    <form
      onSubmit={submit}
      className="rounded-2xl border border-slate-200 bg-white p-2 shadow-soft transition-colors focus-within:border-primary-300"
    >
      <label htmlFor="math-question" className="sr-only">
        Nhập câu hỏi Toán
      </label>
      <textarea
        id="math-question"
        rows={3}
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={
          mode === "study"
            ? "Hỏi lý thuyết, công thức hoặc nhập biểu thức LaTeX..."
            : "Nhập bài toán để nhận gợi ý từng bước..."
        }
        className="max-h-40 min-h-20 w-full resize-none bg-transparent px-3 py-2 text-sm leading-6 text-ink placeholder:text-slate-400 focus:outline-none"
      />
      <div className="flex items-center justify-between gap-3 border-t border-slate-100 px-2 pt-2">
        <span className="hidden items-center gap-1.5 text-xs text-muted sm:flex">
          {mode === "exam" ? (
            <Lightbulb className="h-3.5 w-3.5 text-amber-600" aria-hidden="true" />
          ) : (
            <CornerDownLeft className="h-3.5 w-3.5" aria-hidden="true" />
          )}
          {mode === "exam" ? "Mặc định chỉ hiện gợi ý" : "Enter để gửi, Shift + Enter để xuống dòng"}
        </span>
        <button
          type="submit"
          disabled={disabled || !message.trim()}
          className="ml-auto inline-flex cursor-pointer items-center gap-2 rounded-xl bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-700 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          <span>Gửi câu hỏi</span>
          <Send className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
    </form>
  );
}

