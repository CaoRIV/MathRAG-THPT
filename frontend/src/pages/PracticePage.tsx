import { CheckCircle2, FileQuestion, LoaderCircle } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../lib/api";

const topics = ["Hàm số", "Mũ và logarit", "Nguyên hàm - Tích phân", "Hình học không gian", "Xác suất"];

export function PracticePage() {
  const [topic, setTopic] = useState(topics[0]);
  const [difficulty, setDifficulty] = useState("medium");
  const quiz = useMutation({
    mutationFn: () => api.generateQuiz(topic, difficulty, 3),
  });
  return (
    <div className="mx-auto max-w-5xl">
      <header>
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary-600">Luyện tập có hướng dẫn</p>
        <h1 className="mt-2 font-heading text-3xl font-semibold text-ink">Tạo bộ câu hỏi theo mục tiêu</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">
          Câu hỏi được gắn với tài liệu truy xuất. Chế độ ôn thi ưu tiên gợi ý trước lời giải.
        </p>
      </header>
      <section className="mt-7 grid gap-5 rounded-3xl border border-slate-200 bg-white p-6 shadow-card md:grid-cols-[1fr_220px_auto] md:items-end">
        <label className="block text-sm font-semibold text-ink">
          Chủ đề
          <select value={topic} onChange={(event) => setTopic(event.target.value)} className="mt-2 w-full cursor-pointer rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm font-normal focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100">
            {topics.map((item) => <option key={item}>{item}</option>)}
          </select>
        </label>
        <label className="block text-sm font-semibold text-ink">
          Độ khó
          <select value={difficulty} onChange={(event) => setDifficulty(event.target.value)} className="mt-2 w-full cursor-pointer rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm font-normal focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100">
            <option value="easy">Cơ bản</option>
            <option value="medium">Vận dụng</option>
            <option value="hard">Vận dụng cao</option>
          </select>
        </label>
        <button onClick={() => quiz.mutate()} disabled={quiz.isPending} className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-xl bg-primary-600 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-primary-700 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100 disabled:cursor-wait disabled:bg-primary-400">
          {quiz.isPending ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <FileQuestion className="h-4 w-4" />}
          Tạo bộ câu hỏi
        </button>
      </section>
      {quiz.data && (
        <div className="mt-6 space-y-4" aria-live="polite">
          {quiz.data.questions.map((question, index) => (
            <article key={question.id} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-primary-600">
                <CheckCircle2 className="h-4 w-4" aria-hidden="true" /> Câu {index + 1}
              </div>
              <h2 className="mt-3 font-heading text-lg font-semibold text-ink">{question.prompt}</h2>
              <div className="mt-4 grid gap-2">
                {question.options.map((option, optionIndex) => (
                  <label key={option} className="flex cursor-pointer items-start gap-3 rounded-xl border border-slate-200 px-4 py-3 text-sm text-muted transition-colors hover:border-primary-200 hover:bg-primary-50/30">
                    <input type="radio" name={question.id} value={optionIndex} className="mt-0.5 accent-primary-600" />
                    {option}
                  </label>
                ))}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

