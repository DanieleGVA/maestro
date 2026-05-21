"use client";

import Link from "next/link";
import { useTeacherCourses } from "@/hooks/useApi";
import Alert from "@/components/common/Alert";

/**
 * Class list page.
 * Fetches teacher courses from API. Each course maps to a class view.
 */
export default function ClassesPage() {
  const { data: courses, isLoading, isError, refetch } = useTeacherCourses();

  return (
    <>
      <h1 className="text-2xl font-bold text-page-fg">Le tue classi</h1>

      {isLoading && (
        <p className="mt-6 text-sm text-surface-fg" role="status" aria-live="polite">
          Caricamento...
        </p>
      )}

      {isError && (
        <div className="mt-6">
          <Alert variant="error">
            Errore nel caricamento dei dati.
          </Alert>
          <button
            onClick={() => refetch()}
            className="mt-3 rounded-md bg-focus px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus"
          >
            Riprova
          </button>
        </div>
      )}

      {!isLoading && !isError && courses && (
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {courses.length === 0 ? (
            <p className="text-sm text-surface-fg" role="status">
              Nessuna classe associata al tuo account.
            </p>
          ) : (
            courses.map((course) => (
              <Link
                key={course.id}
                href={`/classes/${course.id}`}
                className="rounded-lg border border-gray-200 p-6 hover:shadow-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
              >
                <h2 className="text-lg font-semibold text-page-fg">
                  {course.class_name || course.name}
                </h2>
                <p className="mt-1 text-sm text-surface-fg">
                  {course.subject}{course.year ? ` - ${course.year}` : ""}
                </p>
                <p className="mt-1 text-sm text-surface-fg">
                  {course.student_count} studenti
                </p>
              </Link>
            ))
          )}
        </div>
      )}
    </>
  );
}
