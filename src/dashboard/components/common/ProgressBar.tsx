"use client";

interface ProgressBarProps {
  current: number;
  total: number;
  label: string;
}

export default function ProgressBar({ current, total, label }: ProgressBarProps) {
  const pct = total > 0 ? Math.round((current / total) * 100) : 0;
  return (
    <div className="w-full">
      <div
        role="progressbar"
        aria-valuenow={current}
        aria-valuemin={0}
        aria-valuemax={total}
        aria-label={label}
        className="h-2 w-full overflow-hidden rounded-full bg-surface-bg"
      >
        <div
          className="h-full rounded-full bg-focus transition-all"
          style={{ width: `${pct}%` }}
          aria-hidden="true"
        />
      </div>
      <span className="mt-1 block text-xs text-surface-fg" aria-hidden="true">
        {current}/{total}
      </span>
    </div>
  );
}
