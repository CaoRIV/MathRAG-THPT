import {
  AlertTriangle,
  ArrowLeft,
  Check,
  CheckCheck,
  ChevronLeft,
  ChevronRight,
  Download,
  FileText,
  LoaderCircle,
  Plus,
  Save,
  ShieldCheck,
  Trash2,
} from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { MathContent } from "../components/math/MathContent";
import { Badge } from "../components/ui/Badge";
import { LoadingDots } from "../components/ui/LoadingDots";
import { api } from "../lib/api";
import { cn } from "../lib/utils";
import type {
  BulkVerificationResult,
  ExamDetail,
  ExamQuestion,
  ExamQuestionDifficulty,
  ExamQuestionOption,
  ExamQuestionType,
  ExamQuestionUpdate,
  ExtractionStatus,
} from "../types/generated/api";

interface QuestionDraft {
  question_type: ExamQuestionType;
  prompt_markdown: string;
  options: ExamQuestionOption[];
  correct_answer: string;
  solution_markdown: string;
  difficulty: ExamQuestionDifficulty | "";
  topics: string;
}

const statusLabels: Record<ExtractionStatus, string> = {
  detected: "Đã nhận diện",
  needs_review: "Cần kiểm duyệt",
  verified: "Đã xác minh",
  rejected: "Đã từ chối",
};

const statusTones: Record<
  ExtractionStatus,
  "cyan" | "amber" | "emerald" | "rose"
> = {
  detected: "cyan",
  needs_review: "amber",
  verified: "emerald",
  rejected: "rose",
};

const questionTypeLabels: Record<ExamQuestionType, string> = {
  multiple_choice: "Trắc nghiệm",
  true_false: "Đúng / sai",
  short_answer: "Trả lời ngắn",
};

function toDraft(question: ExamQuestion): QuestionDraft {
  return {
    question_type: question.question_type,
    prompt_markdown: question.prompt_markdown,
    options: question.options.map((option) => ({ ...option })),
    correct_answer: question.correct_answer ?? "",
    solution_markdown: question.solution_markdown ?? "",
    difficulty: question.difficulty ?? "",
    topics: question.topics.join(", "),
  };
}

function localReviewIssues(draft: QuestionDraft): string[] {
  const issues: string[] = [];
  const answer = draft.correct_answer.trim().toUpperCase();
  const optionKeys = new Set(draft.options.map((option) => option.key.toUpperCase()));
  if (!draft.prompt_markdown.trim()) issues.push("Thiếu nội dung câu hỏi.");
  if (draft.question_type === "multiple_choice") {
    if (draft.options.length < 2) issues.push("Cần ít nhất 2 phương án.");
    if (!answer || !optionKeys.has(answer)) issues.push("Chưa chọn đáp án hợp lệ.");
  } else if (draft.question_type === "true_false") {
    if (draft.options.length !== 4) issues.push("Cần đủ 4 mệnh đề đúng/sai.");
    const normalized = answer.replaceAll("D", "Đ");
    if (normalized.length !== 4 || [...normalized].some((value) => !["Đ", "S"].includes(value))) {
      issues.push("Đáp án phải gồm 4 ký tự Đ hoặc S.");
    }
  } else if (!answer) {
    issues.push("Chưa có đáp án trả lời ngắn.");
  }
  if (!draft.solution_markdown.trim()) issues.push("Thiếu lời giải chi tiết.");
  return issues;
}

function updateExamQuestion(exam: ExamDetail, question: ExamQuestion): ExamDetail {
  return {
    ...exam,
    processing_status:
      exam.processing_status === "approved" || exam.processing_status === "indexed"
        ? "needs_review"
        : exam.processing_status,
    questions: exam.questions.map((item) =>
      item.id === question.id ? question : item,
    ),
  };
}

export function AdminExamReviewPage() {
  const { id = "" } = useParams();
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState("");
  const [draft, setDraft] = useState<QuestionDraft | null>(null);
  const [sourceUrl, setSourceUrl] = useState("");
  const [bulkResult, setBulkResult] = useState<BulkVerificationResult | null>(null);

  const exam = useQuery({
    queryKey: ["admin-exam", id],
    queryFn: () => api.adminExam(id),
    enabled: Boolean(id),
  });
  const source = useQuery({
    queryKey: ["admin-exam-source", id],
    queryFn: () => api.adminExamSource(id),
    enabled: Boolean(id && exam.data?.document_id),
    retry: false,
  });

  useEffect(() => {
    if (!exam.data?.questions.length || selectedId) return;
    const firstPending = exam.data.questions.find(
      (question) => question.extraction_status !== "verified",
    );
    setSelectedId((firstPending ?? exam.data.questions[0]).id);
  }, [exam.data, selectedId]);

  const selectedQuestion = exam.data?.questions.find(
    (question) => question.id === selectedId,
  );

  useEffect(() => {
    if (selectedQuestion) setDraft(toDraft(selectedQuestion));
  }, [selectedQuestion]);

  useEffect(() => {
    if (!source.data) return;
    const url = URL.createObjectURL(source.data);
    setSourceUrl(url);
    return () => {
      URL.revokeObjectURL(url);
      setSourceUrl("");
    };
  }, [source.data]);

  const saveQuestion = useMutation({
    mutationFn: ({
      questionId,
      payload,
    }: {
      questionId: string;
      payload: ExamQuestionUpdate;
    }) => api.updateAdminExamQuestion(id, questionId, payload),
    onSuccess: (question) => {
      queryClient.setQueryData<ExamDetail>(["admin-exam", id], (current) =>
        current ? updateExamQuestion(current, question) : current,
      );
      setBulkResult(null);
    },
  });

  const verifyReady = useMutation({
    mutationFn: () => api.verifyReadyExamQuestions(id),
    onSuccess: (result) => {
      queryClient.setQueryData(["admin-exam", id], result.exam);
      setBulkResult(result);
    },
  });

  const approve = useMutation({
    mutationFn: () => api.approveAdminExam(id),
    onSuccess: (result) => {
      queryClient.setQueryData(["admin-exam", id], result);
      queryClient.invalidateQueries({ queryKey: ["admin-documents"] });
    },
  });

  const counts = useMemo(() => {
    const questions = exam.data?.questions ?? [];
    return {
      verified: questions.filter((item) => item.extraction_status === "verified").length,
      pending: questions.filter((item) => item.extraction_status === "needs_review").length,
      rejected: questions.filter((item) => item.extraction_status === "rejected").length,
    };
  }, [exam.data]);

  const selectedIndex = exam.data?.questions.findIndex((item) => item.id === selectedId) ?? -1;
  const issues = draft ? localReviewIssues(draft) : [];
  const parserWarnings = selectedQuestion?.extraction_status !== "verified" && Array.isArray(selectedQuestion?.metadata.warnings)
    ? selectedQuestion.metadata.warnings.filter(
        (warning): warning is string => typeof warning === "string",
      )
    : [];
  const isPdf = source.data?.type === "application/pdf";
  const canApprove = Boolean(
    exam.data?.question_count && counts.verified === exam.data.question_count,
  );

  function payloadFromDraft(verify: boolean): ExamQuestionUpdate | null {
    if (!draft) return null;
    return {
      question_type: draft.question_type,
      prompt_markdown: draft.prompt_markdown.trim(),
      options: draft.options.map((option) => ({
        key: option.key.trim().toUpperCase(),
        content_markdown: option.content_markdown.trim(),
      })),
      correct_answer: draft.correct_answer.trim() || null,
      solution_markdown: draft.solution_markdown.trim() || null,
      difficulty: draft.difficulty || null,
      topics: draft.topics
        .split(",")
        .map((topic) => topic.trim())
        .filter(Boolean),
      extraction_status: verify ? "verified" : "needs_review",
    };
  }

  function persistQuestion(verify: boolean) {
    if (!selectedQuestion) return;
    const payload = payloadFromDraft(verify);
    if (!payload) return;
    saveQuestion.mutate({ questionId: selectedQuestion.id, payload });
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    persistQuestion(false);
  }

  function moveQuestion(direction: -1 | 1) {
    if (!exam.data) return;
    const next = exam.data.questions[selectedIndex + direction];
    if (next) setSelectedId(next.id);
  }

  function updateOption(index: number, content: string) {
    setDraft((current) =>
      current
        ? {
            ...current,
            options: current.options.map((option, optionIndex) =>
              optionIndex === index
                ? { ...option, content_markdown: content }
                : option,
            ),
          }
        : current,
    );
  }

  function addOption() {
    setDraft((current) => {
      if (!current || current.options.length >= 20) return current;
      const key = String.fromCharCode(65 + current.options.length);
      return {
        ...current,
        options: [...current.options, { key, content_markdown: "" }],
      };
    });
  }

  if (exam.isLoading) {
    return <LoadingDots label="Đang tải dữ liệu kiểm duyệt" />;
  }
  if (exam.isError || !exam.data) {
    return (
      <div role="alert" className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-900">
        Không thể tải đề thi. Hãy kiểm tra backend hoặc quyền Admin.
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[1500px]">
      <Link
        to="/admin/documents"
        className="inline-flex items-center gap-2 text-sm font-semibold text-primary-700 hover:text-primary-800 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden="true" />
        Quay lại kho tài liệu
      </Link>

      <header className="mt-5 rounded-3xl border border-slate-200 bg-white p-6 shadow-card sm:p-8">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="violet">Toán {exam.data.grade}</Badge>
              <Badge tone={exam.data.processing_status === "approved" ? "emerald" : "amber"}>
                {exam.data.processing_status === "approved" ? "Đã duyệt" : "Đang kiểm duyệt"}
              </Badge>
            </div>
            <h1 className="mt-4 font-heading text-2xl font-semibold leading-tight text-ink sm:text-3xl">
              {exam.data.title}
            </h1>
            <p className="mt-2 text-sm text-muted">
              {exam.data.school || "Chưa xác định trường"}
              {exam.data.year ? ` · Năm ${exam.data.year}` : ""}
              {exam.data.duration_minutes ? ` · ${exam.data.duration_minutes} phút` : ""}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => verifyReady.mutate()}
              disabled={verifyReady.isPending || !exam.data.questions.length}
              className="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-ink transition-colors hover:border-primary-200 hover:bg-primary-50 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {verifyReady.isPending ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <CheckCheck className="h-4 w-4" />}
              Xác minh câu hợp lệ
            </button>
            <button
              type="button"
              onClick={() => approve.mutate()}
              disabled={!canApprove || approve.isPending}
              className="inline-flex cursor-pointer items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-emerald-700 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-emerald-100 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              {approve.isPending ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <ShieldCheck className="h-4 w-4" />}
              Duyệt đề thi
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-4">
          {[
            ["Tổng số câu", exam.data.question_count, "text-ink"],
            ["Đã xác minh", counts.verified, "text-emerald-700"],
            ["Cần kiểm duyệt", counts.pending, "text-amber-700"],
            ["Đã từ chối", counts.rejected, "text-rose-700"],
          ].map(([label, value, tone]) => (
            <div key={String(label)} className="rounded-2xl border border-slate-200 bg-slate-50/70 px-4 py-3">
              <p className="text-xs font-medium text-muted">{label}</p>
              <p className={cn("mt-1 font-heading text-2xl font-semibold", String(tone))}>{value}</p>
            </div>
          ))}
        </div>
      </header>

      {(saveQuestion.isError || verifyReady.isError || approve.isError) && (
        <div role="alert" className="mt-5 flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-900">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          <p>{saveQuestion.error?.message || verifyReady.error?.message || approve.error?.message}</p>
        </div>
      )}

      {bulkResult && (
        <div className="mt-5 rounded-2xl border border-primary-100 bg-primary-50/70 p-4 text-sm text-primary-950" role="status">
          Đã xác minh {bulkResult.verified_count} câu. {bulkResult.skipped_count} câu chưa đủ dữ liệu và vẫn cần kiểm duyệt.
        </div>
      )}

      <div className="mt-6 grid items-start gap-6 xl:grid-cols-[minmax(360px,0.85fr)_minmax(0,1.15fr)]">
        <aside className="xl:sticky xl:top-8">
          <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-card">
            <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
              <div>
                <h2 className="font-heading text-base font-semibold text-ink">Tài liệu nguồn</h2>
                <p className="mt-0.5 text-xs text-muted">Đối chiếu với bản Admin đã upload</p>
              </div>
              {sourceUrl && !isPdf && (
                <a href={sourceUrl} download={`${exam.data.title}.docx`} className="grid h-9 w-9 place-items-center rounded-xl border border-slate-200 text-muted hover:bg-slate-50 hover:text-ink" aria-label="Tải file DOCX nguồn">
                  <Download className="h-4 w-4" />
                </a>
              )}
            </div>
            {source.isLoading ? (
              <div className="grid min-h-96 place-items-center"><LoadingDots label="Đang tải file nguồn" /></div>
            ) : sourceUrl && isPdf ? (
              <iframe
                title="Đề thi gốc"
                src={
                  selectedQuestion?.page_number
                    ? `${sourceUrl}#page=${selectedQuestion.page_number}&view=FitH`
                    : sourceUrl
                }
                className="h-[68vh] min-h-[520px] w-full bg-slate-100"
              />
            ) : sourceUrl ? (
              <div className="grid min-h-96 place-items-center p-8 text-center">
                <div>
                  <span className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-primary-50 text-primary-700"><FileText className="h-6 w-6" /></span>
                  <p className="mt-4 font-semibold text-ink">Nguồn DOCX đã sẵn sàng</p>
                  <p className="mt-2 max-w-xs text-sm leading-6 text-muted">Trình duyệt không xem trực tiếp DOCX. Tải file để đối chiếu với câu đang kiểm duyệt.</p>
                  <a href={sourceUrl} download={`${exam.data.title}.docx`} className="mt-5 inline-flex items-center gap-2 rounded-xl bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-700"><Download className="h-4 w-4" /> Tải tài liệu nguồn</a>
                </div>
              </div>
            ) : (
              <div className="grid min-h-80 place-items-center p-8 text-center text-sm text-muted">Không có file nguồn để hiển thị.</div>
            )}
          </div>
        </aside>

        <main className="min-w-0 space-y-5">
          <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-card">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="font-heading text-base font-semibold text-ink">Điều hướng câu hỏi</h2>
                <p className="mt-1 text-xs text-muted">Chọn một câu để xem và chỉnh sửa</p>
              </div>
              <span className="text-xs font-semibold text-muted">{selectedIndex + 1}/{exam.data.questions.length}</span>
            </div>
            <div className="mt-4 grid grid-cols-6 gap-2 sm:grid-cols-10 lg:grid-cols-12">
              {exam.data.questions.map((question) => (
                <button
                  key={question.id}
                  type="button"
                  onClick={() => setSelectedId(question.id)}
                  aria-label={`Câu ${question.question_number}, ${statusLabels[question.extraction_status]}`}
                  aria-current={question.id === selectedId ? "true" : undefined}
                  className={cn(
                    "relative grid aspect-square cursor-pointer place-items-center rounded-xl border text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary-100",
                    question.id === selectedId
                      ? "border-primary-600 bg-primary-600 text-white"
                      : question.extraction_status === "verified"
                        ? "border-emerald-200 bg-emerald-50 text-emerald-800 hover:bg-emerald-100"
                        : question.extraction_status === "rejected"
                          ? "border-rose-200 bg-rose-50 text-rose-800 hover:bg-rose-100"
                          : "border-amber-200 bg-amber-50 text-amber-900 hover:bg-amber-100",
                  )}
                >
                  {question.question_number}
                  <span className="sr-only">{statusLabels[question.extraction_status]}</span>
                  {question.extraction_status === "verified" && <Check className="absolute -right-1 -top-1 h-3.5 w-3.5 rounded-full bg-emerald-600 p-0.5 text-white" aria-hidden="true" />}
                </button>
              ))}
            </div>
          </section>

          {selectedQuestion && draft ? (
            <form onSubmit={submit} className="space-y-5">
              <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-card sm:p-7">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge tone={statusTones[selectedQuestion.extraction_status]}>{statusLabels[selectedQuestion.extraction_status]}</Badge>
                      <Badge tone="slate">{questionTypeLabels[draft.question_type]}</Badge>
                      {selectedQuestion.page_number && <Badge tone="cyan">Trang {selectedQuestion.page_number}</Badge>}
                    </div>
                    <h2 className="mt-3 font-heading text-xl font-semibold text-ink">Câu {selectedQuestion.question_number}</h2>
                  </div>
                  <div className="text-right text-xs text-muted">
                    <p>Độ tin cậy parser</p>
                    <p className="mt-1 font-semibold text-ink">{Math.round((selectedQuestion.extraction_confidence ?? 0) * 100)}%</p>
                  </div>
                </div>

                {(parserWarnings.length > 0 || issues.length > 0) && (
                  <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4">
                    <div className="flex items-center gap-2 text-sm font-semibold text-amber-950"><AlertTriangle className="h-4 w-4" /> Điểm cần kiểm tra</div>
                    <ul className="mt-2 space-y-1 pl-5 text-xs leading-5 text-amber-900">
                      {[...new Set([...issues, ...parserWarnings])].map((warning) => <li key={warning} className="list-disc">{warning}</li>)}
                    </ul>
                  </div>
                )}

                <div className="mt-6 rounded-2xl border border-primary-100 bg-primary-50/40 p-5">
                  <p className="text-xs font-semibold uppercase tracking-wider text-primary-700">Bản xem trước</p>
                  <div className="mt-3"><MathContent>{draft.prompt_markdown || "_Chưa có nội dung câu hỏi._"}</MathContent></div>
                  {draft.options.length > 0 && (
                    <div className="mt-4 grid gap-2 sm:grid-cols-2">
                      {draft.options.map((option) => (
                        <div key={option.key} className={cn("flex gap-3 rounded-xl border bg-white p-3", draft.correct_answer.toUpperCase() === option.key.toUpperCase() ? "border-emerald-300 ring-2 ring-emerald-100" : "border-slate-200")}>
                          <span className="grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-slate-100 text-xs font-bold text-ink">{option.key}</span>
                          <div className="min-w-0"><MathContent>{option.content_markdown || "_Trống_"}</MathContent></div>
                        </div>
                      ))}
                    </div>
                  )}
                  {draft.solution_markdown && (
                    <div className="mt-5 border-t border-primary-100 pt-4">
                      <p className="text-xs font-semibold text-emerald-800">Lời giải</p>
                      <MathContent>{draft.solution_markdown}</MathContent>
                    </div>
                  )}
                </div>
              </section>

              <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-card sm:p-7">
                <h2 className="font-heading text-lg font-semibold text-ink">Chỉnh sửa dữ liệu chuẩn hóa</h2>
                <div className="mt-5 grid gap-5 sm:grid-cols-2">
                  <label className="text-sm font-semibold text-ink">Loại câu hỏi
                    <select value={draft.question_type} onChange={(event) => setDraft({ ...draft, question_type: event.target.value as ExamQuestionType })} className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 font-normal focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100">
                      <option value="multiple_choice">Trắc nghiệm</option><option value="true_false">Đúng / sai</option><option value="short_answer">Trả lời ngắn</option>
                    </select>
                  </label>
                  <label className="text-sm font-semibold text-ink">Độ khó
                    <select value={draft.difficulty} onChange={(event) => setDraft({ ...draft, difficulty: event.target.value as ExamQuestionDifficulty | "" })} className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 font-normal focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100">
                      <option value="">Chưa phân loại</option><option value="easy">Cơ bản</option><option value="medium">Vận dụng</option><option value="hard">Vận dụng cao</option>
                    </select>
                  </label>
                </div>
                <label className="mt-5 block text-sm font-semibold text-ink">Nội dung câu hỏi
                  <textarea rows={5} value={draft.prompt_markdown} onChange={(event) => setDraft({ ...draft, prompt_markdown: event.target.value })} className="mt-2 w-full resize-y rounded-xl border border-slate-200 px-3.5 py-3 font-normal leading-6 focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100" />
                </label>

                {draft.question_type !== "short_answer" && (
                  <div className="mt-5">
                    <div className="flex items-center justify-between gap-3"><p className="text-sm font-semibold text-ink">Phương án / mệnh đề</p><button type="button" onClick={addOption} className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-ink hover:bg-slate-50"><Plus className="h-3.5 w-3.5" /> Thêm</button></div>
                    <div className="mt-3 space-y-3">
                      {draft.options.map((option, index) => (
                        <div key={`${option.key}-${index}`} className="flex items-start gap-3">
                          <span className="mt-2 grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-primary-50 text-xs font-bold text-primary-700">{option.key}</span>
                          <textarea rows={2} value={option.content_markdown} onChange={(event) => updateOption(index, event.target.value)} aria-label={`Nội dung phương án ${option.key}`} className="min-w-0 flex-1 resize-y rounded-xl border border-slate-200 px-3 py-2.5 text-sm leading-6 focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100" />
                          <button type="button" onClick={() => setDraft({ ...draft, options: draft.options.filter((_, optionIndex) => optionIndex !== index) })} className="mt-1 grid h-9 w-9 shrink-0 place-items-center rounded-lg text-muted hover:bg-rose-50 hover:text-rose-700" aria-label={`Xóa phương án ${option.key}`}><Trash2 className="h-4 w-4" /></button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mt-5 grid gap-5 sm:grid-cols-2">
                  <label className="text-sm font-semibold text-ink">Đáp án đúng
                    {draft.question_type === "multiple_choice" ? (
                      <select value={draft.correct_answer} onChange={(event) => setDraft({ ...draft, correct_answer: event.target.value })} className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 font-normal focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100"><option value="">Chọn đáp án</option>{draft.options.map((option) => <option key={option.key} value={option.key}>{option.key}</option>)}</select>
                    ) : (
                      <input value={draft.correct_answer} onChange={(event) => setDraft({ ...draft, correct_answer: event.target.value })} placeholder={draft.question_type === "true_false" ? "Ví dụ: ĐSĐS" : "Nhập đáp án"} className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-3 font-normal focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100" />
                    )}
                  </label>
                  <label className="text-sm font-semibold text-ink">Chủ đề
                    <input value={draft.topics} onChange={(event) => setDraft({ ...draft, topics: event.target.value })} placeholder="Phân cách bằng dấu phẩy" className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-3 font-normal focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100" />
                  </label>
                </div>
                <label className="mt-5 block text-sm font-semibold text-ink">Lời giải chi tiết
                  <textarea rows={7} value={draft.solution_markdown} onChange={(event) => setDraft({ ...draft, solution_markdown: event.target.value })} className="mt-2 w-full resize-y rounded-xl border border-slate-200 px-3.5 py-3 font-normal leading-6 focus:border-primary-400 focus:outline-none focus:ring-4 focus:ring-primary-100" />
                </label>

                <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-5">
                  <div className="flex gap-2">
                    <button type="button" onClick={() => moveQuestion(-1)} disabled={selectedIndex <= 0} className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 text-muted hover:bg-slate-50 hover:text-ink disabled:opacity-30" aria-label="Câu trước"><ChevronLeft className="h-4 w-4" /></button>
                    <button type="button" onClick={() => moveQuestion(1)} disabled={selectedIndex >= exam.data.questions.length - 1} className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 text-muted hover:bg-slate-50 hover:text-ink disabled:opacity-30" aria-label="Câu tiếp theo"><ChevronRight className="h-4 w-4" /></button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        selectedQuestion &&
                        saveQuestion.mutate({
                          questionId: selectedQuestion.id,
                          payload: { extraction_status: "rejected" },
                        })
                      }
                      disabled={saveQuestion.isPending}
                      className="inline-flex items-center gap-2 rounded-xl border border-rose-200 bg-white px-4 py-2.5 text-sm font-semibold text-rose-700 hover:bg-rose-50 disabled:opacity-50"
                    >
                      <Trash2 className="h-4 w-4" /> Loại câu
                    </button>
                    <button type="submit" disabled={saveQuestion.isPending} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-ink hover:bg-slate-50 disabled:opacity-50"><Save className="h-4 w-4" /> Lưu chỉnh sửa</button>
                    <button type="button" onClick={() => persistQuestion(true)} disabled={saveQuestion.isPending || issues.length > 0} className="inline-flex items-center gap-2 rounded-xl bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-700 disabled:cursor-not-allowed disabled:bg-slate-300"><Check className="h-4 w-4" /> Lưu và xác minh</button>
                  </div>
                </div>
              </section>
            </form>
          ) : (
            <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-10 text-center text-sm text-muted">Đề thi chưa có câu hỏi để kiểm duyệt.</div>
          )}
        </main>
      </div>
    </div>
  );
}
