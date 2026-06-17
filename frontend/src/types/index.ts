export type UserRole = "admin" | "user";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface Workspace {
  id: string;
  name: string;
  description?: string | null;
  category?: string | null;
}

export interface DocumentItem {
  id: string;
  workspace_id: string;
  title: string;
  source: string;
  content_type: string;
  category?: string | null;
  status: "pending" | "indexed" | "failed";
  page_count?: number | null;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  document_id?: string | null;
  document_title?: string | null;
  chunk_id?: string | null;
  page_number?: number | null;
  passage: string;
  score?: number | null;
  source_url?: string | null;
}

export interface ChatResponse {
  conversation_id: string;
  message_id: string;
  answer: string;
  citations: Citation[];
  confidence_score: number;
  route: string;
  reflection_cycles: number;
}

export interface AnalyticsSummary {
  total_queries: number;
  average_latency_ms: number;
  retrieval_success_rate: number;
  average_feedback_score?: number | null;
  documents_indexed: number;
}

export interface DocumentAccessStat {
  document_id: string;
  title: string;
  access_count: number;
}
