import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("MathRAG UI error", error, info);
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <main className="grid min-h-screen place-items-center bg-canvas p-6">
        <section className="max-w-md rounded-3xl border border-red-100 bg-white p-8 text-center shadow-soft">
          <AlertTriangle className="mx-auto h-10 w-10 text-red-600" aria-hidden="true" />
          <h1 className="mt-5 font-heading text-2xl font-semibold text-ink">
            Giao diện gặp sự cố
          </h1>
          <p className="mt-3 text-sm leading-6 text-muted">
            Nội dung học của bạn chưa bị thay đổi. Hãy tải lại trang để tiếp tục.
          </p>
          <button
            className="mt-6 inline-flex cursor-pointer items-center gap-2 rounded-xl bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-700 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100"
            onClick={() => window.location.reload()}
          >
            <RotateCcw className="h-4 w-4" aria-hidden="true" />
            Tải lại trang
          </button>
        </section>
      </main>
    );
  }
}

