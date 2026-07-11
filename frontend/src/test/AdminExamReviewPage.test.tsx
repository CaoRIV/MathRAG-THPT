import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { vi } from "vitest";
import { AdminExamReviewPage } from "../pages/AdminExamReviewPage";
import type { ExamDetail } from "../types/generated/api";

const apiMocks = vi.hoisted(() => ({
  adminExam: vi.fn(),
  adminExamSource: vi.fn(),
  updateAdminExamQuestion: vi.fn(),
  verifyReadyExamQuestions: vi.fn(),
  approveAdminExam: vi.fn(),
}));

vi.mock("../lib/api", () => ({ api: apiMocks }));

const exam: ExamDetail = {
  id: "exam-1",
  document_id: "document-1",
  title: "Đề thi thử THPT 2026",
  year: 2026,
  school: "THPT Tích hợp",
  exam_type: "mock",
  duration_minutes: 90,
  question_count: 2,
  grade: 12,
  processing_status: "needs_review",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  metadata: {},
  questions: [
    {
      id: "question-1",
      exam_id: "exam-1",
      question_number: 1,
      question_type: "multiple_choice",
      prompt_markdown: "Tính $1+1$.",
      options: [
        { key: "A", content_markdown: "$2$" },
        { key: "B", content_markdown: "$3$" },
      ],
      correct_answer: "A",
      solution_markdown: "$1+1=2$.",
      topics: ["Số học"],
      formulas: [],
      page_number: 1,
      extraction_status: "needs_review",
      extraction_confidence: 0.95,
      metadata: { warnings: [] },
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    },
    {
      id: "question-2",
      exam_id: "exam-1",
      question_number: 2,
      question_type: "short_answer",
      prompt_markdown: "Tìm $x$.",
      options: [],
      correct_answer: null,
      solution_markdown: null,
      topics: [],
      formulas: [],
      page_number: 2,
      extraction_status: "needs_review",
      extraction_confidence: 0.6,
      metadata: { warnings: ["Chưa ghép được đáp án."] },
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    },
  ],
};

beforeEach(() => {
  apiMocks.adminExam.mockResolvedValue(exam);
  apiMocks.adminExamSource.mockResolvedValue(
    new Blob(["pdf"], { type: "application/pdf" }),
  );
  Object.defineProperty(URL, "createObjectURL", {
    configurable: true,
    value: vi.fn(() => "blob:exam-source"),
  });
  Object.defineProperty(URL, "revokeObjectURL", {
    configurable: true,
    value: vi.fn(),
  });
});

test("shows normalized questions and blocks verification for incomplete data", async () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/admin/exams/exam-1/review"]}>
        <Routes>
          <Route path="/admin/exams/:id/review" element={<AdminExamReviewPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );

  expect(await screen.findByText("Đề thi thử THPT 2026")).toBeInTheDocument();
  const verifyButton = await screen.findByRole("button", { name: "Lưu và xác minh" });
  expect(screen.getByLabelText("Nội dung câu hỏi")).toHaveValue("Tính $1+1$.");
  expect(verifyButton).toBeEnabled();

  fireEvent.click(screen.getByRole("button", { name: /Câu 2,/ }));

  await waitFor(() => {
    expect(screen.getByText("Chưa có đáp án trả lời ngắn.")).toBeInTheDocument();
  });
  expect(screen.getByRole("button", { name: "Lưu và xác minh" })).toBeDisabled();
  expect(await screen.findByTitle("Đề thi gốc")).toHaveAttribute(
    "src",
    "blob:exam-source#page=2&view=FitH",
  );
});
