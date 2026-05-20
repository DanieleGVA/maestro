/**
 * MAESTRO API hook -- typed wrappers around the API client.
 *
 * Endpoint mapping follows IC-12 contract Section 14.4.
 * All responses unwrap the { data, meta } envelope.
 */

import { useCallback, useState } from 'react';
import apiClient from '../services/api';
import type {
  KnowledgeMap,
  Mission,
  Quiz,
  QuizResult,
  StudentProfile,
  StudentNotification,
  NodeDetail,
} from '../types';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

function useApiCall<T>() {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (request: () => Promise<T>): Promise<T | null> => {
    setState({ data: null, loading: true, error: null });
    try {
      const result = await request();
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Errore di comunicazione con il server.';
      setState({ data: null, loading: false, error: message });
      return null;
    }
  }, []);

  return { ...state, execute };
}

// --- Student endpoints ---

export function useKnowledgeMap(studentId: string) {
  const api = useApiCall<KnowledgeMap>();

  const fetch = useCallback(async () => {
    return api.execute(async () => {
      const res = await apiClient.get(`/students/${studentId}/knowledge-map`);
      return res.data.data as KnowledgeMap;
    });
  }, [studentId, api.execute]);

  return { ...api, fetch };
}

export function useNodeDetail(studentId: string, nodeId: string) {
  const api = useApiCall<NodeDetail>();

  const fetch = useCallback(async () => {
    return api.execute(async () => {
      const res = await apiClient.get(`/students/${studentId}/nodes/${nodeId}`);
      return res.data.data as NodeDetail;
    });
  }, [studentId, nodeId, api.execute]);

  return { ...api, fetch };
}

export function useMissions(studentId: string) {
  const api = useApiCall<Mission[]>();

  const fetch = useCallback(async () => {
    return api.execute(async () => {
      const res = await apiClient.get(`/students/${studentId}/missions`);
      return res.data.data as Mission[];
    });
  }, [studentId, api.execute]);

  return { ...api, fetch };
}

export function useStudentProfile(studentId: string) {
  const api = useApiCall<StudentProfile>();

  const fetch = useCallback(async () => {
    return api.execute(async () => {
      const res = await apiClient.get(`/students/${studentId}/profile`);
      return res.data.data as StudentProfile;
    });
  }, [studentId, api.execute]);

  return { ...api, fetch };
}

export function useNotifications(studentId: string) {
  const api = useApiCall<StudentNotification[]>();

  const fetch = useCallback(async () => {
    return api.execute(async () => {
      const res = await apiClient.get(`/students/${studentId}/notifications`);
      return res.data.data as StudentNotification[];
    });
  }, [studentId, api.execute]);

  return { ...api, fetch };
}

// --- Quiz endpoints ---

export function useQuiz() {
  const generateApi = useApiCall<Quiz>();
  const submitApi = useApiCall<QuizResult>();

  const generate = useCallback(
    async (courseId: string, nodeId: string, purpose: 'closure' | 'retention') => {
      return generateApi.execute(async () => {
        const res = await apiClient.post('/quizzes/generate', {
          course_id: courseId,
          node_id: nodeId,
          quiz_purpose: purpose,
        });
        return res.data.data as Quiz;
      });
    },
    [generateApi.execute],
  );

  const submit = useCallback(
    async (
      quizId: string,
      answers: { question_id: string; selected: string }[],
      totalTimeMs: number,
    ) => {
      return submitApi.execute(async () => {
        const res = await apiClient.post(`/quizzes/${quizId}/submit`, {
          answers,
          total_time_ms: totalTimeMs,
        });
        return res.data.data as QuizResult;
      });
    },
    [submitApi.execute],
  );

  return {
    quiz: generateApi.data,
    quizLoading: generateApi.loading,
    quizError: generateApi.error,
    result: submitApi.data,
    resultLoading: submitApi.loading,
    resultError: submitApi.error,
    generate,
    submit,
  };
}

// --- Mission start ---

export function useMissionStart() {
  const api = useApiCall<{ missionId: string }>();

  const start = useCallback(
    async (studentId: string, nodeId: string) => {
      return api.execute(async () => {
        const res = await apiClient.post(
          `/students/${studentId}/missions/${nodeId}/start`,
        );
        return res.data.data as { missionId: string };
      });
    },
    [api.execute],
  );

  return { ...api, start };
}
