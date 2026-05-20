"use client";

import Link from "next/link";
import StateIndicator from "@/components/common/StateIndicator";
import type { MasteryState } from "@/theme/tokens";

interface StudentCardProps {
  studentId: string;
  displayName: string;
  classId: string;
  worstState: MasteryState;
  totalNodes: number;
  consolidatedCount: number;
}

export default function StudentCard({
  studentId,
  displayName,
  classId,
  worstState,
  totalNodes,
  consolidatedCount,
}: StudentCardProps) {
  return (
    <article className="rounded-lg border border-gray-200 p-4 hover:shadow-md">
      <div className="flex items-center justify-between">
        <h3 className="font-medium text-page-fg">{displayName}</h3>
        <StateIndicator state={worstState} size="sm" />
      </div>
      <p className="mt-2 text-sm text-surface-fg">
        {consolidatedCount}/{totalNodes} concetti consolidati
      </p>
      <Link
        href={`/classes/${classId}/students/${studentId}`}
        className="mt-3 inline-block rounded-md bg-focus px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus"
      >
        Dettaglio studente
      </Link>
    </article>
  );
}
