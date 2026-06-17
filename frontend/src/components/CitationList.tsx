import { ExternalLink } from "lucide-react";
import type { Citation } from "../types";

interface CitationListProps {
  citations: Citation[];
}

export function CitationList({ citations }: CitationListProps) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2">
      {citations.map((citation, index) => (
        <div key={`${citation.chunk_id}-${index}`} className="rounded-md border border-line bg-panel p-3">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="truncate text-sm font-medium text-ink">
                [{index + 1}] {citation.document_title ?? citation.source_url ?? "Source"}
              </div>
              <div className="mt-0.5 text-xs text-muted">
                {citation.page_number ? `Page ${citation.page_number}` : "External source"}
                {citation.score ? ` · ${(citation.score * 100).toFixed(0)}% match` : ""}
              </div>
            </div>
            {citation.source_url ? (
              <a className="text-muted hover:text-brand" href={citation.source_url} target="_blank" rel="noreferrer">
                <ExternalLink size={16} />
              </a>
            ) : null}
          </div>
          <p className="mt-2 line-clamp-3 text-sm leading-6 text-muted">{citation.passage}</p>
        </div>
      ))}
    </div>
  );
}
