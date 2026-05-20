"use client";

import Link from "next/link";

/**
 * Lessons list page.
 * MVP: link to upload new lesson.
 */
export default function LessonsPage() {
  return (
    <>
      <h1 className="text-2xl font-bold text-page-fg">Lezioni</h1>

      <div className="mt-6">
        <Link
          href="/lessons/upload"
          className="inline-block rounded-md bg-focus px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus"
        >
          Carica nuova lezione
        </Link>
      </div>

      <div className="mt-6">
        <p className="text-sm text-surface-fg">
          Le lezioni caricate verranno elaborate automaticamente per estrarre i concetti
          e mapparli al grafo della conoscenza del corso.
        </p>
      </div>
    </>
  );
}
