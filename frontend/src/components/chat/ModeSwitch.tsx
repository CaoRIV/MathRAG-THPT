import { BookOpenCheck, TimerReset } from "lucide-react";
import type { ChatMode } from "../../types/generated/api";
import { cn } from "../../lib/utils";

export function ModeSwitch({
  value,
  onChange,
}: {
  value: ChatMode;
  onChange: (mode: ChatMode) => void;
}) {
  return (
    <fieldset>
      <legend className="sr-only">Chọn chế độ học</legend>
      <div className="inline-flex rounded-xl bg-slate-100 p-1">
        {[
          { value: "study" as const, label: "Học tập", icon: BookOpenCheck },
          { value: "exam" as const, label: "Ôn thi", icon: TimerReset },
        ].map((item) => (
          <button
            key={item.value}
            type="button"
            aria-pressed={value === item.value}
            onClick={() => onChange(item.value)}
            className={cn(
              "inline-flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100",
              value === item.value
                ? "bg-white text-primary-700 shadow-sm"
                : "text-muted hover:text-ink",
            )}
          >
            <item.icon className="h-4 w-4" aria-hidden="true" />
            {item.label}
          </button>
        ))}
      </div>
    </fieldset>
  );
}

