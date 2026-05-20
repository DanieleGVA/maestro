"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import type {
  ApiResponse,
  ClassHeatmapResponse,
  IngestionResult,
  KGNode,
  LessonIngestRequest,
  StudentMapResponse,
  TransitionLog,
  TransitionRequest,
} from "@/types";

/** Fetch class heatmap. */
export function useClassHeatmap(classId: string, courseId: string) {
  return useQuery({
    queryKey: ["heatmap", classId, courseId],
    queryFn: async () => {
      const res = await api.get<ClassHeatmapResponse>(
        `/api/v1/kmm/classes/${classId}/heatmap`,
        { params: { course_id: courseId } },
      );
      return res.data;
    },
    enabled: !!classId && !!courseId,
  });
}

/** Fetch student knowledge map. */
export function useStudentMap(studentId: string, courseId: string) {
  return useQuery({
    queryKey: ["studentMap", studentId, courseId],
    queryFn: async () => {
      const res = await api.get<StudentMapResponse>(
        `/api/v1/kmm/students/${studentId}/map`,
        { params: { course_id: courseId } },
      );
      return res.data;
    },
    enabled: !!studentId && !!courseId,
  });
}

/** Fetch KG nodes for a course. */
export function useCourseNodes(courseId: string) {
  return useQuery({
    queryKey: ["courseNodes", courseId],
    queryFn: async () => {
      const res = await api.get<ApiResponse<KGNode[]>>(
        `/api/v1/kg/courses/${courseId}/nodes`,
      );
      return res.data.data;
    },
    enabled: !!courseId,
  });
}

/** Teacher override mutation. */
export function useTeacherOverride(studentId: string, nodeId: string, courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: TransitionRequest) => {
      const res = await api.post<TransitionLog>(
        `/api/v1/kmm/students/${studentId}/nodes/${nodeId}/transition`,
        body,
        { params: { course_id: courseId } },
      );
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["heatmap"] });
      queryClient.invalidateQueries({ queryKey: ["studentMap", studentId] });
    },
  });
}

/** Lesson ingestion mutation. */
export function useIngestLesson(courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: LessonIngestRequest) => {
      const res = await api.post<ApiResponse<IngestionResult>>(
        `/api/v1/kg/courses/${courseId}/lessons/ingest`,
        body,
      );
      return res.data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courseNodes", courseId] });
    },
  });
}

/** Confirm or reject a concept mapping. */
export function useConfirmMapping() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ mappingId, action }: { mappingId: string; action: "confirm" | "reject" }) => {
      const res = await api.post(`/api/v1/kg/mappings/${mappingId}/confirm`, { action });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courseNodes"] });
    },
  });
}
