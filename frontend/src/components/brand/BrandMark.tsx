import { cn } from "../../lib/utils";

export function BrandMark({
  size = "md",
  className,
}: {
  size?: "sm" | "md" | "lg";
  className?: string;
}) {
  const sizes = {
    sm: "h-10 w-10 rounded-xl",
    md: "h-12 w-12 rounded-2xl",
    lg: "h-20 w-20 rounded-3xl",
  };
  const robotSizes = {
    sm: "h-5 w-5 -bottom-1 -right-1",
    md: "h-6 w-6 -bottom-1.5 -right-1.5",
    lg: "h-9 w-9 -bottom-2 -right-2",
  };

  return (
    <span className={cn("relative inline-block shrink-0", className)}>
      <img
        src="/brand/math-logo.png"
        alt="Biểu trưng MathRAG THPT"
        className={cn(
          "block object-cover shadow-card ring-1 ring-white/80",
          sizes[size],
        )}
      />
      <span
        className={cn(
          "absolute grid place-items-center overflow-hidden rounded-full bg-white p-0.5 shadow-md ring-2 ring-white",
          robotSizes[size],
        )}
        aria-hidden="true"
      >
        <img
          src="/brand/chatbot-robot.png"
          alt=""
          className="h-full w-full object-contain"
        />
      </span>
    </span>
  );
}

export function ChatbotAvatar({
  size = "md",
  className,
}: {
  size?: "md" | "lg";
  className?: string;
}) {
  return (
    <span
      className={cn(
        "grid shrink-0 place-items-center overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200",
        size === "lg" ? "h-16 w-16 p-1.5" : "h-10 w-10 p-1",
        className,
      )}
    >
      <img
        src="/brand/chatbot-robot.png"
        alt="Robot trợ lý MathRAG"
        className="h-full w-full object-contain"
      />
    </span>
  );
}
