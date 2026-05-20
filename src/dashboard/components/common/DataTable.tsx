"use client";

import type { ReactNode } from "react";

interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  caption: string;
  getRowKey: (row: T) => string;
}

/**
 * Accessible data table with proper scope attributes.
 * Per accessibility-mvp-spec.md Section 6.5.
 */
export default function DataTable<T>({ columns, rows, caption, getRowKey }: DataTableProps<T>) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm" aria-label={caption}>
        <caption className="sr-only">{caption}</caption>
        <thead>
          <tr className="border-b-2 border-surface-bg">
            {columns.map((col) => (
              <th
                key={col.key}
                scope="col"
                className="px-3 py-2 text-left font-semibold text-page-fg"
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={getRowKey(row)} className="border-b border-surface-bg hover:bg-surface-bg/50">
              {columns.map((col) => (
                <td key={col.key} className="px-3 py-2">
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
