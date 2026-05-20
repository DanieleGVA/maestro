"use client";

import { useState } from "react";
import Modal from "@/components/common/Modal";
import StateIndicator from "@/components/common/StateIndicator";
import { MASTERY_STATES, type MasteryState } from "@/theme/tokens";

interface OverrideModalProps {
  isOpen: boolean;
  onClose: () => void;
  studentName: string;
  nodeLabel: string;
  currentState: MasteryState;
  onSubmit: (targetState: MasteryState, motivation: string) => void;
  isPending: boolean;
}

const MIN_MOTIVATION_LENGTH = 20;

/**
 * Modal for teacher override of a student node state (F11.12).
 * Requires motivation >= 20 characters.
 */
export default function OverrideModal({
  isOpen,
  onClose,
  studentName,
  nodeLabel,
  currentState,
  onSubmit,
  isPending,
}: OverrideModalProps) {
  const [targetState, setTargetState] = useState<MasteryState>(currentState);
  const [motivation, setMotivation] = useState("");
  const motivationValid = motivation.length >= MIN_MOTIVATION_LENGTH;
  const canSubmit = targetState !== currentState && motivationValid && !isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (canSubmit) {
      onSubmit(targetState, motivation);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Override stato studente">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <p className="text-sm text-surface-fg">
            Studente: <strong>{studentName}</strong>
          </p>
          <p className="text-sm text-surface-fg">
            Concetto: <strong>{nodeLabel}</strong>
          </p>
          <div className="mt-2 flex items-center gap-2">
            <span className="text-sm text-surface-fg">Stato attuale:</span>
            <StateIndicator state={currentState} size="sm" />
          </div>
        </div>

        <div>
          <label htmlFor="target-state" className="mb-1 block text-sm font-medium text-page-fg">
            Nuovo stato
          </label>
          <select
            id="target-state"
            value={targetState}
            onChange={(e) => setTargetState(e.target.value as MasteryState)}
            className="w-full rounded-md border border-border-input px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
          >
            {MASTERY_STATES.map((s) => (
              <option key={s} value={s} disabled={s === currentState}>
                {s === currentState ? `${s} (attuale)` : s}
              </option>
            ))}
          </select>
        </div>

        {targetState !== currentState && (
          <div className="flex items-center gap-2 rounded-md bg-surface-bg p-3" aria-live="polite">
            <span className="text-sm text-surface-fg">Transizione:</span>
            <StateIndicator state={currentState} size="sm" />
            <span aria-hidden="true" className="text-surface-fg">&rarr;</span>
            <span className="sr-only">a</span>
            <StateIndicator state={targetState} size="sm" />
          </div>
        )}

        <div>
          <label htmlFor="motivation" className="mb-1 block text-sm font-medium text-page-fg">
            Motivazione (minimo {MIN_MOTIVATION_LENGTH} caratteri)
          </label>
          <textarea
            id="motivation"
            value={motivation}
            onChange={(e) => setMotivation(e.target.value)}
            rows={3}
            aria-describedby="motivation-hint"
            aria-invalid={motivation.length > 0 && !motivationValid}
            className="w-full rounded-md border border-border-input px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
            placeholder="Descrivi il motivo dell'override..."
          />
          <p id="motivation-hint" className="mt-1 text-xs text-surface-fg">
            {motivation.length}/{MIN_MOTIVATION_LENGTH} caratteri minimi
            {motivation.length > 0 && !motivationValid && (
              <span className="ml-2 text-red-700" role="alert">
                Motivazione troppo breve
              </span>
            )}
          </p>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-md px-4 py-2 text-sm text-surface-fg hover:bg-surface-bg focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
          >
            Annulla
          </button>
          <button
            type="submit"
            disabled={!canSubmit}
            className="rounded-md bg-focus px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus"
          >
            {isPending ? "Salvataggio..." : "Conferma override"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
