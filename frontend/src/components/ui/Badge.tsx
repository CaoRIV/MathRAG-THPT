import type { ReactNode } from "react";
import { cn } from "../../lib/utils";

export function Badge({
  children,
  tone = "violet",
}: {
  children: ReactNode;
  tone?: "violet" | "cyan" | "amber" | "emerald" | "rose" | "slate";
}) {
  const tones = {
    violet: "bg-primary-50 text-primary-700 ring-primary-100",
    cyan: "bg-cyan-50 text-cyan-800 ring-cyan-100",
    amber: "bg-amber-50 text-amber-800 ring-amber-100",
    emerald: "bg-emerald-50 text-emerald-800 ring-emerald-100",
    rose: "bg-rose-50 text-rose-800 ring-rose-100",
    slate: "bg-slate-50 text-slate-700 ring-slate-200",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset",
        tones[tone],
      )}
    >
      {children}
    </span>
  );
}

