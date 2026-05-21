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
  TeacherCourse,
  ClassStudentRow,
  SafeguardingAlert,
} from "@/types";

/** Fetch teacher's courses (used as class list). */
export function useTeacherCourses() {
  return useQuery({
    queryKey: ["teacherCourses"],
    queryFn: async () => {
      const res = await api.get<TeacherCourse[]>("/api/v1/teachers/me/courses");
      // The API may return the array directly or wrapped in { data: [...] }
      const data = Array.isArray(res.data) ? res.data : (res.data as unknown as ApiResponse<TeacherCourse[]>).data;
      return data;
    },
  });
}

/** Fetch per-student mastery rows for a class. */
export function useClassStudents(classId: string, courseId?: string) {
  const effectiveCourseId = courseId ?? classId;
  return useQuery({
    queryKey: ["classStudents", classId, effectiveCourseId],
    queryFn: async () => {
      const res = await api.get<ClassStudentRow[]>(
        `/api/v1/kmm/classes/${classId}/students`,
        { params: { course_id: effectiveCourseId } },
      );
      const data = Array.isArray(res.data) ? res.data : (res.data as unknown as ApiResponse<ClassStudentRow[]>).data;
      return data;
    },
    enabled: !!classId,
  });
}

/** Fetch safeguarding / wellbeing alerts. */
export function useAlerts() {
  return useQuery({
    queryKey: ["safeguardingAlerts"],
    queryFn: async () => {
      const res = await api.get<SafeguardingAlert[]>("/api/v1/safeguarding/alerts");
      const data = Array.isArray(res.data) ? res.data : (res.data as unknown as ApiResponse<SafeguardingAlert[]>).data;
      return data;
    },
  });
}

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
