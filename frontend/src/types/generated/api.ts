export type ChatMode = "study" | "exam";
export type AssistanceLevel = "hint" | "guided" | "full";
export type ContentType = "theory" | "formula" | "example" | "exam" | "solution";

export interface SearchFilters {
  grade?: number | null;
  topics?: string[];
  content_types?: ContentType[];
}

export interface ChatRequest {
  message: string;
  mode: ChatMode;
  conversation_id?: string | null;
  assistance_level?: AssistanceLevel | null;
  filters?: SearchFilters;
}

export interface Citation {
  id: string;
  document_id: string;
  chunk_id: string;
  title: string;
  label: string;
  source_url?: string | null;
  page_number?: number | null;
}

export interface Evidence {
  chunk_id: string;
  document_id: string;
  title: string;
  topic: string;
  content_type: string;
  excerpt: string;
  score: number;
  score_breakdown: Record<string, number>;
}

export interface RelatedDocument {
  id: string;
  title: string;
  topic: string;
  content_type: string;
  source_url?: string | null;
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  mode: ChatMode;
  assistance_level?: AssistanceLevel | null;
  citations: Citation[];
  evidence: Evidence[];
  related_documents: RelatedDocument[];
  detected_formulas: string[];
  confidence: number;
  fallback_status?: string | null;
}

export interface SearchResponse {
  query: string;
  items: Evidence[];
  total: number;
  page: number;
  page_size: number;
  detected_formulas: string[];
}

export interface TopicItem {
  slug: string;
  name: string;
  description: string;
  document_count: number;
  accent: string;
}

export interface DocumentSection {
  id: string;
  heading?: string | null;
  content: string;
  content_type: string;
  page_number?: number | null;
  formulas: string[];
}

export interface DocumentDetail {
  id: string;
  title: string;
  description?: string | null;
  grade: number;
  topic: string;
  content_type: string;
  source_url?: string | null;
  sections: DocumentSection[];
  formulas: string[];
  related_documents: RelatedDocument[];
}

export interface QuizQuestion {
  id: string;
  prompt: string;
  options: string[];
  source_chunk_id: string;
}

export interface QuizResponse {
  id: string;
  topic: string;
  difficulty: string;
  assistance_level: AssistanceLevel;
  questions: QuizQuestion[];
}

export interface ReadinessResponse {
  status: string;
  checks: Record<string, { status: string; detail: string }>;
}

export type UserRole = "user" | "admin";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface AdminDocument {
  id: string;
  title: string;
  original_filename: string;
  grade: number;
  topic: string;
  content_type: string;
  chunk_count: number;
  exam_id?: string | null;
  exam_processing_status?: ExamProcessingStatus | null;
  exam_parse_report?: ExamParseReport | null;
  uploaded_by: string;
  created_at: string;
}

export interface AdminDocumentList {
  items: AdminDocument[];
  total: number;
}

export type ExamProcessingStatus =
  | "uploaded"
  | "parsing"
  | "needs_review"
  | "approved"
  | "indexed"
  | "failed";

export interface ExamParseReport {
  exam_id: string;
  document_id: string;
  processing_status: ExamProcessingStatus;
  detected_questions: number;
  answers_matched: number;
  solutions_matched: number;
  formulas_detected: number;
  created_questions: number;
  updated_questions: number;
  preserved_verified_questions: number;
  removed_stale_questions: number;
  questions_needing_review: number;
  warnings: string[];
}
