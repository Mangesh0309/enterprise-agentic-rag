import { useEffect, useState } from "react";
import { Activity, Clock, FileText, Star, Target } from "lucide-react";
import { apiFetch } from "../../api/client";
import { Card } from "../../components/Card";
import { StatTile } from "../../components/StatTile";
import type { AnalyticsSummary, DocumentAccessStat } from "../../types";

export function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [documents, setDocuments] = useState<DocumentAccessStat[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiFetch<AnalyticsSummary>("/analytics/summary"),
      apiFetch<DocumentAccessStat[]>("/analytics/documents"),
    ])
      .then(([summaryData, documentData]) => {
        setSummary(summaryData);
        setDocuments(documentData);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Unable to load analytics"));
  }, []);

  if (error) {
    return <div className="p-6 text-sm text-red-700">{error}</div>;
  }

  return (
    <section className="min-h-screen p-4 md:p-6">
      <div className="mb-5">
        <h2 className="text-xl font-semibold text-ink">Analytics</h2>
        <p className="mt-1 text-sm text-muted">Operational performance and usage quality</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <StatTile label="Queries" value={summary?.total_queries ?? 0} icon={<Activity size={18} />} />
        <StatTile label="Latency" value={`${summary?.average_latency_ms ?? 0} ms`} icon={<Clock size={18} />} />
        <StatTile
          label="Retrieval"
          value={`${Math.round((summary?.retrieval_success_rate ?? 0) * 100)}%`}
          icon={<Target size={18} />}
        />
        <StatTile label="Feedback" value={summary?.average_feedback_score ?? "-"} icon={<Star size={18} />} />
        <StatTile label="Documents" value={summary?.documents_indexed ?? 0} icon={<FileText size={18} />} />
      </div>

      <Card className="mt-5 overflow-hidden">
        <div className="border-b border-line px-4 py-3">
          <h3 className="font-semibold text-ink">Frequently accessed documents</h3>
        </div>
        <div className="divide-y divide-line">
          {documents.map((document) => (
            <div key={document.document_id} className="flex items-center justify-between gap-4 px-4 py-3">
              <span className="min-w-0 truncate text-sm font-medium text-ink">{document.title}</span>
              <span className="rounded-md bg-panel px-2 py-1 text-xs text-muted">{document.access_count}</span>
            </div>
          ))}
          {documents.length === 0 ? <div className="px-4 py-8 text-sm text-muted">No citation traffic yet.</div> : null}
        </div>
      </Card>
    </section>
  );
}
