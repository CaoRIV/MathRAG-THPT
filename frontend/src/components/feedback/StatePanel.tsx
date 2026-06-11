import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

export function StatePanel({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-card">
      <span className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-primary-50 text-primary-600">
        <Icon className="h-6 w-6" aria-hidden="true" />
      </span>
      <h2 className="mt-4 font-heading text-lg font-semibold text-ink">{title}</h2>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-muted">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </section>
  );
}
