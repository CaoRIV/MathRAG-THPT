export function LoadingDots({ label = "Đang xử lý" }: { label?: string }) {
  return (
    <span className="inline-flex items-center gap-1" role="status" aria-label={label}>
      {[0, 1, 2].map((index) => (
        <span
          key={index}
          className="h-1.5 w-1.5 animate-pulse-soft rounded-full bg-primary-500"
          style={{ animationDelay: `${index * 160}ms` }}
        />
      ))}
    </span>
  );
}

