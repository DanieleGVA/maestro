/**
 * MAESTRO Student App -- TypeScript type definitions.
 *
 * Aligned with IC-12 contract (interface-contracts.md Section 14)
 * and accessibility-mvp-spec.md mastery tokens.
 */

// --- Mastery state machine (6 canonical states per CLAUDE.md) ---

export type MasteryState =
  | 'non_introdotto'
  | 'introdotto'
  | 'lacuna'
  | 'in_recupero'
  | 'da_consolidare'
  | 'consolidato';

// --- Knowledge graph nodes ---

export interface KGNode {
  id: string;
  label: string;
  type: 'macro' | 'micro';
  state: MasteryState;
  parentId: string | null;
  prerequisiteIds: string[];
  dependentIds: string[];
}

export interface MacroNode extends KGNode {
  type: 'macro';
  microNodes: MicroNodeSummary[];
  rollupState: MasteryState;
  totalMicros: int;
  microsPerState: Record<MasteryState, number>;
}

type int = number;

export interface MicroNodeSummary {
  id: string;
  label: string;
  state: MasteryState;
}

// --- Student knowledge map (from GET /students/{id}/knowledge-map) ---

export interface KnowledgeMap {
  studentId: string;
  courseId: string;
  macroNodes: MacroNode[];
  totalNodes: number;
  nodesConsolidato: number;
  nodesLacuna: number;
}

// --- Node detail (from GET /students/{id}/content/{contentId}) ---

export interface NodeDetail {
  nodeId: string;
  label: string;
  state: MasteryState;
  description: string;
  prerequisiteIds: string[];
  dependentIds: string[];
  retentionCheckDue: string | null;
  missionId: string | null;
  content: GeneratedContent | null;
}

// --- Missions (from GET /students/{id}/missions) ---

export interface Mission {
  id: string;
  nodeId: string;
  nodeLabel: string;
  state: 'lacuna' | 'in_recupero';
  progress: {
    current: number;
    total: number;
  };
  quizId: string | null;
}

// --- Quiz (from POST /quizzes/generate, POST /quizzes/{id}/submit) ---

export interface QuizQuestion {
  id: string;
  text: string;
  options: QuizOption[];
  codeBlock: string | null;
}

export interface QuizOption {
  id: string;
  text: string;
  codeBlock: string | null;
}

export interface Quiz {
  quizId: string;
  nodeId: string;
  purpose: 'closure' | 'retention';
  questions: QuizQuestion[];
}

export interface QuizResult {
  quizId: string;
  score: number;
  correctCount: number;
  totalQuestions: number;
  transitionTriggered: string | null;
  feedbackMessage: string;
  perQuestion: QuestionFeedback[];
}

export interface QuestionFeedback {
  questionId: string;
  correct: boolean;
  explanation: string;
  selectedOptionId: string;
  correctOptionId: string;
}

// --- Generated content ---

export interface GeneratedContent {
  id: string;
  type: 'review_document' | 'remediation_path' | 'quiz_generation' | 'retention_check';
  blocks: ContentBlock[];
  summary: string;
}

export interface ContentBlock {
  conceptNodeId: string;
  conceptLabel: string;
  ilTuoErrore: {
    text: string;
    codeErrato: string | null;
  } | null;
  percheSe: {
    text: string;
  } | null;
  comeSiFaGiusto: {
    text: string;
    codeCorretto: string | null;
  } | null;
  ricordati: {
    text: string;
  } | null;
}

// --- Student profile ---

export interface StudentProfile {
  id: string;
  schoolYear: number;
  status: string;
  adaptationProfile: ContentAdaptationProfile | null;
  activatedAt: string | null;
}

export interface ContentAdaptationProfile {
  visuale: number;
  audio: number;
  pratico: number;
  lettura: number;
  dialogo: number;
}

// --- Auth ---

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

// --- API response envelope (per IC-12 Section 14.2) ---

export interface ApiResponse<T> {
  data: T;
  meta: {
    request_id: string;
    timestamp: string;
  };
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
  };
  meta: {
    request_id: string;
    timestamp: string;
  };
}

// --- Notifications ---

export interface StudentNotification {
  id: string;
  type: 'mission_available' | 'quiz_ready' | 'retention_due' | 'content_ready';
  title: string;
  message: string;
  read: boolean;
  createdAt: string;
  relatedNodeId: string | null;
}
