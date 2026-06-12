import type {
  AdminDocument,
  AdminDocumentList,
  AuthResponse,
  ChatRequest,
  ChatResponse,
  DocumentDetail,
  ExamParseReport,
  QuizResponse,
  ReadinessResponse,
  SearchFilters,
  SearchResponse,
  TopicItem,
  User,
} from "../types/generated/api";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message);
  }
}

const TOKEN_KEY = "mathrag_access_token";

export function getAccessToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  try {
    const token = getAccessToken();
    const isFormData = init?.body instanceof FormData;
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        ...(!isFormData ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...init?.headers,
      },
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      throw new ApiError(payload?.detail ?? "Yêu cầu không thành công.", response.status);
    }
    return response.json() as Promise<T>;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError("Không thể kết nối tới máy chủ MathRAG.");
  }
}

export const api = {
  register: (payload: { email: string; full_name: string; password: string }) =>
    request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  login: (payload: { email: string; password: string }) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  me: () => request<User>("/auth/me"),
  chat: (payload: ChatRequest) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  search: (
    query: string,
    filters: SearchFilters = { grade: 12 },
    includeScores = true,
  ) =>
    request<SearchResponse>("/search", {
      method: "POST",
      body: JSON.stringify({
        query,
        filters,
        page: 1,
        page_size: 20,
        include_scores: includeScores,
      }),
    }),
  topics: () => request<TopicItem[]>("/topics"),
  document: (id: string) => request<DocumentDetail>(`/documents/${id}`),
  readiness: () => request<ReadinessResponse>("/ready"),
  generateQuiz: (topic: string, difficulty: string, questionCount: number) =>
    request<QuizResponse>("/quizzes/generate", {
      method: "POST",
      body: JSON.stringify({
        topic,
        difficulty,
        question_count: questionCount,
        assistance_level: "hint",
      }),
    }),
  adminDocuments: () => request<AdminDocumentList>("/admin/documents"),
  uploadAdminDocument: (formData: FormData) =>
    request<AdminDocument>("/admin/documents/upload", {
      method: "POST",
      body: formData,
    }),
  parseAdminExamDocument: (documentId: string) =>
    request<ExamParseReport>(`/admin/documents/${documentId}/parse-exam`, {
      method: "POST",
    }),
};
