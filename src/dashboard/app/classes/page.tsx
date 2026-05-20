"use client";

import Link from "next/link";

/**
 * Class list page.
 * MVP: single class. Links to class detail (heatmap).
 */
export default function ClassesPage() {
  // MVP: hardcoded single class. Production: fetch from API.
  const classes = [
    { id: "class-1", name: "3A Informatica", courseId: "course-1", studentCount: 25 },
  ];

  return (
    <>
      <h1 className="text-2xl font-bold text-page-fg">Le tue classi</h1>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {classes.map((cls) => (
          <Link
            key={cls.id}
            href={`/classes/${cls.id}?courseId=${cls.courseId}`}
            className="rounded-lg border border-gray-200 p-6 hover:shadow-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
          >
            <h2 className="text-lg font-semibold text-page-fg">{cls.name}</h2>
            <p className="mt-1 text-sm text-surface-fg">{cls.studentCount} studenti</p>
          </Link>
        ))}
      </div>
    </>
  );
}
