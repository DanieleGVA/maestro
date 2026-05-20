/**
 * MAESTRO student state hook.
 *
 * Aggregates knowledge map, missions, and profile data for the current student.
 * Used by the home dashboard and map screens.
 */

import { useState, useEffect, useCallback } from 'react';
import apiClient from '../services/api';
import type { KnowledgeMap, Mission, StudentProfile } from '../types';

interface StudentState {
  knowledgeMap: KnowledgeMap | null;
  missions: Mission[];
  profile: StudentProfile | null;
  loading: boolean;
  error: string | null;
}

export function useStudentState(studentId: string | null) {
  const [state, setState] = useState<StudentState>({
    knowledgeMap: null,
    missions: [],
    profile: null,
    loading: false,
    error: null,
  });

  const refresh = useCallback(async () => {
    if (!studentId) return;

    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const [mapRes, missionsRes, profileRes] = await Promise.all([
        apiClient.get(`/students/${studentId}/knowledge-map`),
        apiClient.get(`/students/${studentId}/missions`),
        apiClient.get(`/students/${studentId}/profile`),
      ]);

      setState({
        knowledgeMap: mapRes.data.data as KnowledgeMap,
        missions: (missionsRes.data.data ?? []) as Mission[],
        profile: profileRes.data.data as StudentProfile,
        loading: false,
        error: null,
      });
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Errore nel caricamento dei dati.';
      setState((prev) => ({ ...prev, loading: false, error: message }));
    }
  }, [studentId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { ...state, refresh };
}
