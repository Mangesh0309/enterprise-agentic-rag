import type { ReactNode } from "react";

interface StatTileProps {
  label: string;
  value: string | number;
  icon: ReactNode;
}

export function StatTile({ label, value, icon }: StatTileProps) {
  return (
    <div className="rounded-lg border border-line bg-white p-4">
      <div className="flex items-center justify-between gap-3">
        <span className="text-sm text-muted">{label}</span>
        <span className="text-brand">{icon}</span>
      </div>
      <div className="mt-3 text-2xl font-semibold text-ink">{value}</div>
    </div>
  );
}
