"use client";

import { useState } from "react";
import type { LessonIngestRequest } from "@/types";

interface LessonUploadProps {
  onSubmit: (data: LessonIngestRequest) => void;
  isPending: boolean;
}

/**
 * Form for uploading lesson content (text only for MVP).
 */
export default function LessonUpload({ onSubmit, isPending }: LessonUploadProps) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [materialType, setMaterialType] = useState("lesson");

  const canSubmit = title.trim().length > 0 && content.trim().length > 0 && !isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (canSubmit) {
      onSubmit({ title: title.trim(), content: content.trim(), material_type: materialType });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="lesson-title" className="mb-1 block text-sm font-medium text-page-fg">
          Titolo della lezione
        </label>
        <input
          id="lesson-title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full rounded-md border border-border-input px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
          placeholder="Es. Introduzione alle variabili in Python"
          autoComplete="off"
        />
      </div>

      <div>
        <label htmlFor="material-type" className="mb-1 block text-sm font-medium text-page-fg">
          Tipo di materiale
        </label>
        <select
          id="material-type"
          value={materialType}
          onChange={(e) => setMaterialType(e.target.value)}
          className="w-full rounded-md border border-border-input px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
        >
          <option value="lesson">Lezione</option>
          <option value="textbook">Libro di testo</option>
          <option value="exercise">Esercizio</option>
        </select>
      </div>

      <div>
        <label htmlFor="lesson-content" className="mb-1 block text-sm font-medium text-page-fg">
          Contenuto della lezione
        </label>
        <textarea
          id="lesson-content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={12}
          className="w-full rounded-md border border-border-input px-3 py-2 font-mono text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
          placeholder="Incolla qui il testo della lezione..."
        />
        <p className="mt-1 text-xs text-surface-fg">
          {content.length} caratteri
        </p>
      </div>

      <button
        type="submit"
        disabled={!canSubmit}
        className="rounded-md bg-focus px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus"
      >
        {isPending ? "Elaborazione in corso..." : "Carica lezione"}
      </button>
    </form>
  );
}
