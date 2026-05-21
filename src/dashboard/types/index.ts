import type { MasteryState } from "@/theme/tokens";

/** API response envelope per interface-contracts.md Section 14.2. */
export interface ApiResponse<T> {
  data: T;
  meta: {
    request_id: string;
    timestamp: string;
  };
}

/** API error response per interface-contracts.md Section 14.3. */
export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  meta: {
    request_id: string;
    timestamp: string;
  };
}

/** KMM node state per backend schemas.py. */
export interface NodeState {
  student_id: string;
  node_id: string;
  course_id: string;
  current_state: MasteryState;
  previous_state: MasteryState | null;
  state_since: string;
  attempt_count: number;
  last_quiz_score: number | null;
  last_quiz_at: string | null;
  next_retention_check: string | null;
  retention_checks_passed: number;
}

/** Student knowledge map response. */
export interface StudentMapResponse {
  student_id: string;
  course_id: string;
  nodes: NodeState[];
}

/** Transition log entry. */
export interface TransitionLog {
  id: number;
  student_id: string;
  node_id: string;
  course_id: string;
  previous_state: string;
  new_state: string;
  trigger_type: string;
  triggered_by: string | null;
  quiz_score: number | null;
  motivation: string | null;
  created_at: string;
}

/** Class heatmap -- per-node state counts. */
export interface ClassNodeSummary {
  node_id: string;
  counts_per_state: Record<string, number>;
  total_students: number;
}

export interface ClassHeatmapResponse {
  course_id: string;
  node_summaries: ClassNodeSummary[];
}

/** KG node. */
export interface KGNode {
  id: string;
  course_id: string;
  node_type: "macro" | "micro";
  label_it: string;
  description: string | null;
  difficulty: number;
  macro_id: string | null;
  is_active: boolean;
  sort_order: number;
}

/** Lesson ingestion result. */
export interface IngestionResult {
  material_id: string;
  chunk_count: number;
  mapping_count: number;
  candidates_for_review: CandidateMapping[];
  unmapped_chunks: number;
}

export interface CandidateMapping {
  node_id: string;
  node_type: "macro" | "micro";
  label_it: string;
  description: string | null;
  embedding_similarity: number;
  llm_confidence: number;
  composite_score: number;
  confidence_level: string;
  llm_explanation: string | null;
}

/** Teacher override request body. */
export interface TransitionRequest {
  target_state: MasteryState;
  motivation: string;
}

/** Lesson ingest request body. */
export interface LessonIngestRequest {
  title: string;
  content: string;
  material_type: string;
}

/** Per-student heatmap row for the class heatmap grid view. */
export interface StudentHeatmapRow {
  student_id: string;
  display_name: string;
  states: Record<string, MasteryState>;
}

/** Auth user claims from JWT. */
export interface UserClaims {
  sub: string;
  preferred_username: string;
  email: string;
  realm_access: {
    roles: string[];
  };
}

/** Teacher course returned by GET /api/v1/teachers/me/courses. */
export interface TeacherCourse {
  id: string;
  name: string;
  subject: string;
  class_name: string;
  student_count: number;
  year: string;
}

/** Per-student mastery row from GET /api/v1/kmm/classes/{classId}/students. */
export interface ClassStudentRow {
  student_id: string;
  display_name: string;
  states: Record<string, MasteryState>;
}

/** Safeguarding alert from GET /api/v1/safeguarding/alerts. */
export interface SafeguardingAlert {
  id: string;
  student_pseudo_id: string;
  severity: "high" | "medium" | "low";
  phrase: string;
  context: string;
  timestamp: string;
  read: boolean;
}
