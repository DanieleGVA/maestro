"use client";

import type { ReactNode } from "react";

interface AlertProps {
  variant: "info" | "warning" | "error";
  children: ReactNode;
}

const VARIANT_STYLES = {
  info: "border-focus bg-blue-50 text-blue-900",
  warning: "border-maestro-in-recupero-border bg-orange-50 text-orange-900",
  error: "border-maestro-lacuna-border bg-red-50 text-red-900",
} as const;

export default function Alert({ variant, children }: AlertProps) {
  return (
    <div
      role="alert"
      aria-live={variant === "error" ? "assertive" : "polite"}
      className={`rounded-md border-l-4 p-4 ${VARIANT_STYLES[variant]}`}
    >
      {children}
    </div>
  );
}
