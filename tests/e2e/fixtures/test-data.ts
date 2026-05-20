/**
 * Shared test data fixtures for MAESTRO E2E tests.
 *
 * All student data uses pseudonymised IDs (no real PII per CLAUDE.md).
 * Mastery states follow the canonical 6-state machine.
 */

import type { MasteryState } from "./types";

// ---------------------------------------------------------------------------
// Auth credentials (test-only, never used in production)
// ---------------------------------------------------------------------------

export const TEACHER_CREDENTIALS = {
  username: "prof.rossi",
  password: "TestPassword123!",
} as const;

export const STUDENT_CREDENTIALS = {
  username: "studente.test01",
  password: "TestPassword456!",
} as const;

export const ADMIN_CREDENTIALS = {
  username: "admin.scuola",
  password: "AdminPassword789!",
} as const;

// ---------------------------------------------------------------------------
// JWT tokens (pre-built test tokens, base64-encoded payloads)
// ---------------------------------------------------------------------------

function buildTestJwt(payload: Record<string, unknown>): string {
  const header = btoa(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const body = btoa(JSON.stringify({
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 3600,
    ...payload,
  }));
  const signature = "test-signature";
  return `${header}.${body}.${signature}`;
}

export const TEACHER_TOKEN = buildTestJwt({
  sub: "teacher-uuid-001",
  preferred_username: "prof.rossi",
  email: "rossi@scuola-test.it",
  realm_access: { roles: ["teacher"] },
});

export const STUDENT_TOKEN = buildTestJwt({
  sub: "student-uuid-001",
  preferred_username: "studente.test01",
  email: "student01@scuola-test.it",
  realm_access: { roles: ["student"] },
  student_id: "student-uuid-001",
});

export const ADMIN_TOKEN = buildTestJwt({
  sub: "admin-uuid-001",
  preferred_username: "admin.scuola",
  email: "admin@scuola-test.it",
  realm_access: { roles: ["admin"] },
});

// ---------------------------------------------------------------------------
// Course & class data
// ---------------------------------------------------------------------------

export const TEST_COURSE = {
  id: "course-test-001",
  name: "Informatica 3A",
  school_year: 2025,
} as const;

export const TEST_CLASS = {
  id: "class-test-001",
  name: "3A Informatica",
  courseId: TEST_COURSE.id,
  studentCount: 5,
} as const;

// ---------------------------------------------------------------------------
// KG nodes (macro + micro)
// ---------------------------------------------------------------------------

export const MACRO_NODES = [
  {
    id: "macro-001",
    course_id: TEST_COURSE.id,
    node_type: "macro" as const,
    label_it: "Variabili e Tipi di Dato",
    description: "Concetti fondamentali sulle variabili e i tipi di dato in Python",
    difficulty: 1,
    macro_id: null,
    is_active: true,
    sort_order: 1,
  },
  {
    id: "macro-002",
    course_id: TEST_COURSE.id,
    node_type: "macro" as const,
    label_it: "Strutture di Controllo",
    description: "If/else, cicli for e while",
    difficulty: 2,
    macro_id: null,
    is_active: true,
    sort_order: 2,
  },
  {
    id: "macro-003",
    course_id: TEST_COURSE.id,
    node_type: "macro" as const,
    label_it: "Funzioni",
    description: "Definizione e uso delle funzioni",
    difficulty: 3,
    macro_id: null,
    is_active: true,
    sort_order: 3,
  },
  {
    id: "macro-004",
    course_id: TEST_COURSE.id,
    node_type: "macro" as const,
    label_it: "Liste e Tuple",
    description: "Strutture dati sequenziali",
    difficulty: 2,
    macro_id: null,
    is_active: true,
    sort_order: 4,
  },
  {
    id: "macro-005",
    course_id: TEST_COURSE.id,
    node_type: "macro" as const,
    label_it: "Dizionari",
    description: "Strutture dati associative",
    difficulty: 3,
    macro_id: null,
    is_active: true,
    sort_order: 5,
  },
];

// ---------------------------------------------------------------------------
// Student data (pseudonymised)
// ---------------------------------------------------------------------------

export const TEST_STUDENTS = [
  { id: "student-uuid-001", display_name: "STU-001", school_year: 3 },
  { id: "student-uuid-002", display_name: "STU-002", school_year: 3 },
  { id: "student-uuid-003", display_name: "STU-003", school_year: 3 },
  { id: "student-uuid-004", display_name: "STU-004", school_year: 3 },
  { id: "student-uuid-005", display_name: "STU-005", school_year: 3 },
];

// ---------------------------------------------------------------------------
// Student mastery states (per-student per-node)
// ---------------------------------------------------------------------------

export function buildStudentNodeStates(
  studentId: string,
  stateMap: Record<string, MasteryState>,
) {
  return Object.entries(stateMap).map(([nodeId, state]) => ({
    student_id: studentId,
    node_id: nodeId,
    course_id: TEST_COURSE.id,
    current_state: state,
    previous_state: null,
    state_since: "2025-09-01T08:00:00Z",
    attempt_count: 0,
    last_quiz_score: null,
    last_quiz_at: null,
    next_retention_check: state === "da_consolidare" ? "2025-12-01T08:00:00Z" : null,
    retention_checks_passed: state === "consolidato" ? 3 : 0,
  }));
}

export const STUDENT_001_STATES: Record<string, MasteryState> = {
  "macro-001": "consolidato",
  "macro-002": "da_consolidare",
  "macro-003": "in_recupero",
  "macro-004": "lacuna",
  "macro-005": "non_introdotto",
};

export const STUDENT_002_STATES: Record<string, MasteryState> = {
  "macro-001": "consolidato",
  "macro-002": "consolidato",
  "macro-003": "da_consolidare",
  "macro-004": "introdotto",
  "macro-005": "non_introdotto",
};

// ---------------------------------------------------------------------------
// Class heatmap data
// ---------------------------------------------------------------------------

export const CLASS_HEATMAP = {
  course_id: TEST_COURSE.id,
  node_summaries: MACRO_NODES.map((node) => ({
    node_id: node.id,
    counts_per_state: {
      non_introdotto: 1,
      introdotto: 1,
      lacuna: 1,
      in_recupero: 0,
      da_consolidare: 1,
      consolidato: 1,
    },
    total_students: 5,
  })),
};

// ---------------------------------------------------------------------------
// Student heatmap rows (for ClassHeatmap grid)
// ---------------------------------------------------------------------------

export const STUDENT_HEATMAP_ROWS = [
  {
    student_id: "student-uuid-001",
    display_name: "STU-001",
    states: STUDENT_001_STATES,
  },
  {
    student_id: "student-uuid-002",
    display_name: "STU-002",
    states: STUDENT_002_STATES,
  },
];

// ---------------------------------------------------------------------------
// Quiz data
// ---------------------------------------------------------------------------

export const QUIZ_QUESTIONS = [
  {
    id: "q-001",
    text: "Quale parola chiave si usa per definire una variabile in Python?",
    options: [
      { id: "q-001-a", text: "var", codeBlock: null },
      { id: "q-001-b", text: "let", codeBlock: null },
      { id: "q-001-c", text: "Non serve una parola chiave", codeBlock: null },
      { id: "q-001-d", text: "define", codeBlock: null },
    ],
    codeBlock: null,
  },
  {
    id: "q-002",
    text: "Qual e' il tipo di dato del valore `3.14`?",
    options: [
      { id: "q-002-a", text: "int", codeBlock: null },
      { id: "q-002-b", text: "float", codeBlock: null },
      { id: "q-002-c", text: "str", codeBlock: null },
      { id: "q-002-d", text: "double", codeBlock: null },
    ],
    codeBlock: null,
  },
  {
    id: "q-003",
    text: "Cosa stampa il seguente codice?",
    options: [
      { id: "q-003-a", text: "5", codeBlock: null },
      { id: "q-003-b", text: "10", codeBlock: null },
      { id: "q-003-c", text: "Errore", codeBlock: null },
      { id: "q-003-d", text: "None", codeBlock: null },
    ],
    codeBlock: "x = 5\nprint(x + 5)",
  },
];

export const TEST_QUIZ = {
  quizId: "quiz-test-001",
  nodeId: "macro-001",
  purpose: "closure" as const,
  questions: QUIZ_QUESTIONS,
};

export const QUIZ_RESULT_PASS = {
  quiz_id: "quiz-test-001",
  score: 100,
  correct_count: 3,
  total_questions: 3,
  transition_triggered: "quiz_superato",
  feedback_message: "Ottimo lavoro! Hai superato il quiz.",
};

export const QUIZ_RESULT_FAIL = {
  quiz_id: "quiz-test-001",
  score: 33,
  correct_count: 1,
  total_questions: 3,
  transition_triggered: "quiz_fallito",
  feedback_message: "Non ti preoccupare, e' un'opportunita' per ripassare con un approccio diverso.",
};

// ---------------------------------------------------------------------------
// Missions data
// ---------------------------------------------------------------------------

export const TEST_MISSIONS = [
  {
    id: "mission-001",
    nodeId: "macro-003",
    nodeLabel: "Funzioni",
    state: "in_recupero" as const,
    progress: { current: 1, total: 3 },
    quizId: "quiz-test-002",
  },
  {
    id: "mission-002",
    nodeId: "macro-004",
    nodeLabel: "Liste e Tuple",
    state: "lacuna" as const,
    progress: { current: 0, total: 3 },
    quizId: "quiz-test-003",
  },
];

// ---------------------------------------------------------------------------
// Node detail data
// ---------------------------------------------------------------------------

export const NODE_DETAIL_LACUNA = {
  nodeId: "macro-004",
  label: "Liste e Tuple",
  state: "lacuna" as const,
  description: "Le liste e le tuple sono strutture dati fondamentali in Python.",
  prerequisiteIds: ["macro-001"],
  dependentIds: ["macro-005"],
  retentionCheckDue: null,
  missionId: "mission-002",
  content: null,
};

export const NODE_DETAIL_CONSOLIDATO = {
  nodeId: "macro-001",
  label: "Variabili e Tipi di Dato",
  state: "consolidato" as const,
  description: "Concetti fondamentali sulle variabili e i tipi di dato in Python.",
  prerequisiteIds: [],
  dependentIds: ["macro-002", "macro-004"],
  retentionCheckDue: null,
  missionId: null,
  content: null,
};

export const NODE_DETAIL_DA_CONSOLIDARE = {
  nodeId: "macro-002",
  label: "Strutture di Controllo",
  state: "da_consolidare" as const,
  description: "If/else, cicli for e while.",
  prerequisiteIds: ["macro-001"],
  dependentIds: ["macro-003"],
  retentionCheckDue: "2025-12-01T08:00:00Z",
  missionId: null,
  content: null,
};

// ---------------------------------------------------------------------------
// Lesson ingestion data
// ---------------------------------------------------------------------------

export const LESSON_INGEST_REQUEST = {
  title: "Introduzione alle variabili in Python",
  content: "Una variabile in Python e' un nome che fa riferimento a un valore in memoria. A differenza di altri linguaggi, Python non richiede la dichiarazione esplicita del tipo.",
  material_type: "lesson",
};

export const LESSON_INGEST_RESPONSE = {
  material_id: "mat-test-001",
  chunk_count: 3,
  mapping_count: 2,
  candidates_for_review: [
    {
      node_id: "macro-001",
      node_type: "macro" as const,
      label_it: "Variabili e Tipi di Dato",
      description: "Concetti fondamentali sulle variabili",
      embedding_similarity: 0.92,
      llm_confidence: 0.88,
      composite_score: 0.9,
      confidence_level: "high",
      llm_explanation: "Il testo tratta esplicitamente di variabili Python",
    },
    {
      node_id: "micro-001",
      node_type: "micro" as const,
      label_it: "Assegnazione variabili",
      description: "Come assegnare valori a variabili",
      embedding_similarity: 0.85,
      llm_confidence: 0.78,
      composite_score: 0.81,
      confidence_level: "medium",
      llm_explanation: null,
    },
  ],
  unmapped_chunks: 1,
};

// ---------------------------------------------------------------------------
// Wellbeing alerts data
// ---------------------------------------------------------------------------

export const WELLBEING_ALERTS = [
  {
    id: "alert-001",
    studentPseudoId: "STU-003",
    phrase: "non capisco niente, non ce la faccio piu'",
    timestamp: "2025-10-15T14:32:00Z",
    read: false,
  },
  {
    id: "alert-002",
    studentPseudoId: "STU-001",
    phrase: "e' tutto inutile",
    timestamp: "2025-10-14T09:15:00Z",
    read: true,
  },
];

// ---------------------------------------------------------------------------
// Knowledge map summary (student home screen)
// ---------------------------------------------------------------------------

export const STUDENT_KNOWLEDGE_MAP_SUMMARY = {
  studentId: "student-uuid-001",
  courseId: TEST_COURSE.id,
  macroNodes: MACRO_NODES.map((n, i) => ({
    ...n,
    type: "macro" as const,
    state: Object.values(STUDENT_001_STATES)[i],
    parentId: null,
    prerequisiteIds: [],
    dependentIds: [],
    microNodes: [],
    rollupState: Object.values(STUDENT_001_STATES)[i],
    totalMicros: 3,
    microsPerState: {
      non_introdotto: 0,
      introdotto: 0,
      lacuna: 0,
      in_recupero: 0,
      da_consolidare: 0,
      consolidato: 3,
    },
  })),
  totalNodes: 5,
  nodesConsolidato: 1,
  nodesLacuna: 1,
};
