import { Calculator, FunctionSquare, GraduationCap } from "lucide-react";
import { BrandMark } from "../brand/BrandMark";

const prompts = [
  {
    icon: FunctionSquare,
    title: "Tra cứu công thức",
    prompt: "Công thức đổi cơ số logarit và điều kiện áp dụng là gì?",
  },
  {
    icon: Calculator,
    title: "Hiểu bản chất",
    prompt: "Giải thích vì sao dấu đạo hàm quyết định tính đơn điệu.",
  },
  {
    icon: GraduationCap,
    title: "Luyện thi THPT",
    prompt: "Cho mình một bài tương tự về diện tích hình phẳng và chỉ gợi ý.",
  },
];

export function EmptyChat({ onPrompt }: { onPrompt: (prompt: string) => void }) {
  return (
    <section className="py-8 text-center sm:py-14">
      <BrandMark size="lg" className="mx-auto" />
      <h1 className="mt-5 font-heading text-2xl font-semibold tracking-tight text-ink sm:text-3xl">
        Học Toán với căn cứ rõ ràng
      </h1>
      <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-muted sm:text-base">
        Hỏi bằng tiếng Việt hoặc LaTeX. MathRAG tìm lý thuyết, công thức và ví dụ
        liên quan trước khi trả lời.
      </p>
      <div className="mx-auto mt-8 grid max-w-3xl gap-3 text-left md:grid-cols-3">
        {prompts.map((item) => (
          <button
            key={item.title}
            onClick={() => onPrompt(item.prompt)}
            className="group cursor-pointer rounded-2xl border border-slate-200 bg-white p-4 transition-colors duration-200 hover:border-primary-200 hover:bg-primary-50/40 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100"
          >
            <item.icon className="h-5 w-5 text-primary-600" aria-hidden="true" />
            <span className="mt-3 block text-sm font-semibold text-ink">{item.title}</span>
            <span className="mt-1.5 block text-xs leading-5 text-muted">{item.prompt}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
