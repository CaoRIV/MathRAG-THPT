import {
  CheckCircle2,
  FileSearch,
  FileText,
  FileUp,
  FolderOpen,
  ShieldCheck,
  TriangleAlert,
  UploadCloud,
  X,
} from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRef, useState, type DragEvent, type FormEvent } from "react";
import { api } from "../lib/api";
import { Badge } from "../components/ui/Badge";
import { LoadingDots } from "../components/ui/LoadingDots";
import { cn, contentLabels } from "../lib/utils";
import type {
  ExamParseReport,
  ExamProcessingStatus,
} from "../types/generated/api";

const topics = [
  "Hàm số",
  "Mũ và logarit",
  "Nguyên hàm - Tích phân",
  "Hình học không gian",
  "Xác suất",
  "Đề thi THPT",
];

const examStatusLabels: Record<ExamProcessingStatus, string> = {
  uploaded: "Chưa phân tích",
  parsing: "Đang phân tích",
  needs_review: "Cần kiểm duyệt",
  approved: "Đã duyệt",
  indexed: "Đã lập chỉ mục",
  failed: "Phân tích lỗi",
};

const examStatusTones: Record<
  ExamProcessingStatus,
  "violet" | "cyan" | "amber" | "emerald" | "rose" | "slate"
> = {
  uploaded: "slate",
  parsing: "cyan",
  needs_review: "amber",
  approved: "emerald",
  indexed: "emerald",
  failed: "rose",
};

export function AdminDocumentsPage() {
  const queryClient = useQueryClient();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [title, setTitle] = useState("");
  const [topic, setTopic] = useState(topics[0]);
  const [grade, setGrade] = useState("12");
  const [contentType, setContentType] = useState("theory");
  const [description, setDescription] = useState("");
  const [parseReport, setParseReport] = useState<ExamParseReport | null>(null);
  const documents = useQuery({
    queryKey: ["admin-documents"],
    queryFn: api.adminDocuments,
  });
  const upload = useMutation({
    mutationFn: api.uploadAdminDocument,
    onSuccess: (document) => {
      queryClient.invalidateQueries({ queryKey: ["admin-documents"] });
      setParseReport(document.exam_parse_report ?? null);
      setFile(null);
      setTitle("");
      setDescription("");
    },
  });
  const parseExam = useMutation({
    mutationFn: api.parseAdminExamDocument,
    onSuccess: (report) => {
      setParseReport(report);
      queryClient.invalidateQueries({ queryKey: ["admin-documents"] });
    },
  });

  function selectFile(selected?: File) {
    if (!selected) return;
    setFile(selected);
    if (!title) setTitle(selected.name.replace(/\.(pdf|docx)$/i, ""));
  }

  function drop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    selectFile(event.dataTransfer.files[0]);
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    formData.append("topic", topic);
    formData.append("grade", grade);
    formData.append("content_type", contentType);
    if (description.trim()) formData.append("description", description.trim());
    upload.mutate(formData);
  }

  const fieldClass = "mt-2 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-3 text-sm font-normal text-ink transition-colors focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100";

  return (
    <div className="mx-auto max-w-6xl">
      <header className="flex flex-wrap items-end justify-between gap-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary-600">
            <ShieldCheck className="h-4 w-4" aria-hidden="true" />
            Khu vực quản trị
          </div>
          <h1 className="mt-2 font-heading text-3xl font-semibold text-ink">
            Quản lý kho tài liệu chính
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">
            Tải PDF hoặc DOCX đã được phê duyệt. Nội dung sẽ được phân đoạn, lập chỉ
            mục và đưa vào truy xuất của chatbot.
          </p>
        </div>
        <Badge tone="emerald">Chỉ quản trị viên</Badge>
      </header>

      <div className="mt-8 grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
        <form onSubmit={submit} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card sm:p-8">
          <h2 className="font-heading text-xl font-semibold text-ink">Thêm tài liệu mới</h2>
          <p className="mt-1 text-sm text-muted">Giới hạn 25 MB cho mỗi file.</p>
          <div
            onDragOver={(event) => {
              event.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={drop}
            className={cn(
              "mt-6 rounded-2xl border-2 border-dashed p-6 text-center transition-colors",
              isDragging
                ? "border-primary-400 bg-primary-50"
                : file
                  ? "border-emerald-300 bg-emerald-50/60"
                  : "border-slate-200 bg-slate-50/60",
            )}
          >
            <input ref={inputRef} type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" className="sr-only" onChange={(event) => selectFile(event.target.files?.[0])} />
            {file ? (
              <div className="flex items-center gap-3 text-left">
                <span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-white text-emerald-700 shadow-sm">
                  <FileText className="h-5 w-5" aria-hidden="true" />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold text-ink">{file.name}</p>
                  <p className="mt-1 text-xs text-muted">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <button type="button" onClick={() => setFile(null)} aria-label="Bỏ file đã chọn" className="grid h-9 w-9 cursor-pointer place-items-center rounded-xl text-muted hover:bg-white hover:text-red-700 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-red-100">
                  <X className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <>
                <span className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-primary-100 text-primary-700">
                  <UploadCloud className="h-5 w-5" aria-hidden="true" />
                </span>
                <p className="mt-4 text-sm font-semibold text-ink">Kéo thả PDF hoặc DOCX vào đây</p>
                <p className="mt-1 text-xs text-muted">hoặc chọn file từ máy tính</p>
                <button type="button" onClick={() => inputRef.current?.click()} className="mt-4 inline-flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-ink transition-colors hover:border-primary-200 hover:bg-primary-50 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100">
                  <FolderOpen className="h-4 w-4" aria-hidden="true" />
                  Chọn tài liệu
                </button>
              </>
            )}
          </div>

          <div className="mt-6 grid gap-5 sm:grid-cols-2">
            <label className="text-sm font-semibold text-ink">
              Tên tài liệu
              <input required minLength={2} maxLength={300} value={title} onChange={(event) => setTitle(event.target.value)} className={fieldClass} />
            </label>
            <label className="text-sm font-semibold text-ink">
              Chủ đề
              <select value={topic} onChange={(event) => setTopic(event.target.value)} className={fieldClass}>
                {topics.map((item) => <option key={item}>{item}</option>)}
              </select>
            </label>
            <label className="text-sm font-semibold text-ink">
              Khối lớp
              <select value={grade} onChange={(event) => setGrade(event.target.value)} className={fieldClass}>
                <option value="10">Toán 10</option>
                <option value="11">Toán 11</option>
                <option value="12">Toán 12</option>
              </select>
            </label>
            <label className="text-sm font-semibold text-ink">
              Loại nội dung
              <select value={contentType} onChange={(event) => setContentType(event.target.value)} className={fieldClass}>
                <option value="theory">Lý thuyết</option>
                <option value="formula">Công thức</option>
                <option value="example">Ví dụ</option>
                <option value="exam">Đề thi</option>
                <option value="solution">Lời giải</option>
              </select>
            </label>
          </div>
          <label className="mt-5 block text-sm font-semibold text-ink">
            Mô tả ngắn
            <textarea rows={3} maxLength={2000} value={description} onChange={(event) => setDescription(event.target.value)} className={`${fieldClass} resize-none`} placeholder="Phạm vi kiến thức hoặc nguồn tài liệu..." />
          </label>
          {upload.isError && <div role="alert" className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{upload.error.message}</div>}
          {upload.isSuccess && <div role="status" className="mt-5 flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"><CheckCircle2 className="h-4 w-4" /> Tài liệu đã được lập chỉ mục thành công.</div>}
          <button disabled={!file || upload.isPending} className="mt-6 inline-flex w-full cursor-pointer items-center justify-center gap-2 rounded-xl bg-primary-600 px-5 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-primary-700 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100 disabled:cursor-not-allowed disabled:bg-slate-300">
            <FileUp className="h-4 w-4" aria-hidden="true" />
            {upload.isPending ? "Đang đọc và lập chỉ mục..." : "Tải lên kho chính"}
          </button>
        </form>

        <aside className="space-y-4">
          <div className="rounded-3xl border border-primary-100 bg-primary-50/70 p-5">
            <h2 className="text-sm font-semibold text-primary-950">Quy trình xử lý</h2>
            <ol className="mt-4 space-y-4">
              {["Kiểm tra loại và dung lượng file", "Trích xuất văn bản và công thức", "Chia đoạn theo cấu trúc nội dung", "Cập nhật hybrid retrieval và FAISS"].map((item, index) => (
                <li key={item} className="flex gap-3 text-xs leading-5 text-primary-900">
                  <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-white font-semibold text-primary-700">{index + 1}</span>
                  {item}
                </li>
              ))}
            </ol>
          </div>
        </aside>
      </div>

      <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-card sm:p-8">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="font-heading text-xl font-semibold text-ink">Tài liệu đã upload</h2>
            <p className="mt-1 text-sm text-muted">{documents.data?.total ?? 0} tài liệu trong kho quản trị</p>
          </div>
          {documents.isLoading && <LoadingDots />}
        </div>
        {parseReport && (
          <div
            className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950"
            role="status"
            aria-live="polite"
          >
            <div className="flex items-start gap-3">
              <FileSearch className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
              <div>
                <p className="font-semibold">
                  Đã phát hiện {parseReport.detected_questions} câu hỏi
                </p>
                <p className="mt-1 leading-6">
                  Ghép được {parseReport.answers_matched} đáp án,{" "}
                  {parseReport.solutions_matched} lời giải và{" "}
                  {parseReport.formulas_detected} công thức. Còn{" "}
                  {parseReport.questions_needing_review} câu cần kiểm duyệt.
                </p>
              </div>
            </div>
          </div>
        )}
        {parseExam.isError && (
          <div
            className="mt-5 flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-900"
            role="alert"
          >
            <TriangleAlert className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            <p>{parseExam.error.message}</p>
          </div>
        )}
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[900px] border-separate border-spacing-0 text-left text-sm">
            <thead>
              <tr className="text-xs uppercase tracking-wider text-muted">
                <th className="border-b border-slate-200 px-3 py-3 font-semibold">Tài liệu</th>
                <th className="border-b border-slate-200 px-3 py-3 font-semibold">Chủ đề</th>
                <th className="border-b border-slate-200 px-3 py-3 font-semibold">Loại</th>
                <th className="border-b border-slate-200 px-3 py-3 font-semibold">Chunks</th>
                <th className="border-b border-slate-200 px-3 py-3 font-semibold">Xử lý đề</th>
                <th className="border-b border-slate-200 px-3 py-3 font-semibold">Ngày tải</th>
              </tr>
            </thead>
            <tbody>
              {documents.data?.items.map((document) => (
                <tr key={document.id}>
                  <td className="border-b border-slate-100 px-3 py-4">
                    <p className="font-semibold text-ink">{document.title}</p>
                    <p className="mt-1 text-xs text-muted">{document.original_filename}</p>
                  </td>
                  <td className="border-b border-slate-100 px-3 py-4 text-muted">Toán {document.grade} · {document.topic}</td>
                  <td className="border-b border-slate-100 px-3 py-4"><Badge tone="slate">{contentLabels[document.content_type] ?? document.content_type}</Badge></td>
                  <td className="border-b border-slate-100 px-3 py-4 text-muted">{document.chunk_count}</td>
                  <td className="border-b border-slate-100 px-3 py-4">
                    {document.content_type === "exam" ? (
                      <div className="flex min-w-40 flex-col items-start gap-2">
                        {document.exam_processing_status && (
                          <Badge tone={examStatusTones[document.exam_processing_status]}>
                            {examStatusLabels[document.exam_processing_status]}
                          </Badge>
                        )}
                        <button
                          type="button"
                          onClick={() => {
                            setParseReport(null);
                            parseExam.mutate(document.id);
                          }}
                          disabled={
                            parseExam.isPending && parseExam.variables === document.id
                          }
                          className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-ink transition-colors hover:border-primary-200 hover:bg-primary-50 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100 disabled:cursor-wait disabled:text-muted"
                        >
                          <FileSearch className="h-3.5 w-3.5" aria-hidden="true" />
                          {parseExam.isPending && parseExam.variables === document.id
                            ? "Đang phân tích..."
                            : document.exam_id
                              ? "Phân tích lại"
                              : "Phân tích đề"}
                        </button>
                      </div>
                    ) : (
                      <span className="text-xs text-muted">Không áp dụng</span>
                    )}
                  </td>
                  <td className="border-b border-slate-100 px-3 py-4 text-muted">{new Intl.DateTimeFormat("vi-VN").format(new Date(document.created_at))}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {documents.data?.items.length === 0 && <div className="py-10 text-center text-sm text-muted">Chưa có tài liệu quản trị nào được tải lên.</div>}
        </div>
      </section>
    </div>
  );
}
