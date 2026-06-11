import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AssistantAnswer } from "../components/chat/AssistantAnswer";
import type { ChatResponse } from "../types/generated/api";

const response: ChatResponse = {
  conversation_id: "conversation",
  answer: "Dùng công thức $\\int x^n dx$ [1].",
  mode: "study",
  assistance_level: null,
  citations: [
    {
      id: "S1",
      document_id: "doc-1",
      chunk_id: "chunk-1",
      title: "Bảng nguyên hàm",
      label: "[1]",
    },
  ],
  evidence: [
    {
      chunk_id: "chunk-1",
      document_id: "doc-1",
      title: "Bảng nguyên hàm",
      topic: "Nguyên hàm - Tích phân",
      content_type: "formula",
      excerpt: "Nội dung",
      score: 0.9,
      score_breakdown: {},
    },
  ],
  related_documents: [],
  detected_formulas: [],
  confidence: 0.9,
  fallback_status: null,
};

test("shows answer citation and retrieval transparency control", () => {
  render(
    <MemoryRouter>
      <AssistantAnswer response={response} />
    </MemoryRouter>,
  );
  expect(screen.getByText("MathRAG trả lời")).toBeInTheDocument();
  expect(screen.getByText(/\[1\] Bảng nguyên hàm/)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Xem cách truy xuất/ })).toBeInTheDocument();
});
