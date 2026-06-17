import { FormEvent, useEffect, useState } from "react";
import { FileUp, FolderPlus, RefreshCw, Trash2 } from "lucide-react";
import { apiFetch } from "../../api/client";
import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import type { DocumentItem, Workspace } from "../../types";

export function DocumentsPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [workspaceId, setWorkspaceId] = useState("");
  const [workspaceName, setWorkspaceName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [category, setCategory] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);

  async function load() {
    const [workspaceData, documentData] = await Promise.all([
      apiFetch<Workspace[]>("/workspaces"),
      apiFetch<DocumentItem[]>(workspaceId ? `/documents?workspace_id=${workspaceId}` : "/documents"),
    ]);
    setWorkspaces(workspaceData);
    setDocuments(documentData);
  }

  useEffect(() => {
    load().catch((err) => setError(err instanceof Error ? err.message : "Unable to load documents"));
  }, [workspaceId]);

  async function createWorkspace(event: FormEvent) {
    event.preventDefault();
    if (!workspaceName.trim()) return;
    setIsBusy(true);
    setError(null);
    try {
      await apiFetch<Workspace>("/workspaces", {
        method: "POST",
        body: JSON.stringify({ name: workspaceName, category }),
      });
      setWorkspaceName("");
      setCategory("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Workspace creation failed");
    } finally {
      setIsBusy(false);
    }
  }

  async function upload(event: FormEvent) {
    event.preventDefault();
    if (!workspaceId || !file) return;
    setIsBusy(true);
    setError(null);
    try {
      const form = new FormData();
      form.set("workspace_id", workspaceId);
      form.set("category", category);
      form.set("file", file);
      await apiFetch<DocumentItem>("/documents/upload", {
        method: "POST",
        body: form,
      });
      setFile(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsBusy(false);
    }
  }

  async function remove(documentId: string) {
    await apiFetch(`/documents/${documentId}`, { method: "DELETE" });
    await load();
  }

  return (
    <section className="min-h-screen p-4 md:p-6">
      <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-ink">Documents</h2>
          <p className="mt-1 text-sm text-muted">{documents.length} indexed or pending items</p>
        </div>
        <Button variant="secondary" icon={<RefreshCw size={16} />} onClick={() => load()}>
          Refresh
        </Button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[360px_1fr]">
        <div className="space-y-4">
          <Card className="p-4">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-muted">Workspace</h3>
            <form className="mt-4 space-y-3" onSubmit={createWorkspace}>
              <input
                className="h-10 w-full rounded-md border border-line px-3 text-sm outline-none focus:border-brand"
                value={workspaceName}
                onChange={(event) => setWorkspaceName(event.target.value)}
                placeholder="Engineering"
              />
              <input
                className="h-10 w-full rounded-md border border-line px-3 text-sm outline-none focus:border-brand"
                value={category}
                onChange={(event) => setCategory(event.target.value)}
                placeholder="Category"
              />
              <Button className="w-full" disabled={isBusy} icon={<FolderPlus size={16} />}>
                Create
              </Button>
            </form>
          </Card>

          <Card className="p-4">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-muted">Upload</h3>
            <form className="mt-4 space-y-3" onSubmit={upload}>
              <select
                className="h-10 w-full rounded-md border border-line bg-white px-3 text-sm outline-none focus:border-brand"
                value={workspaceId}
                onChange={(event) => setWorkspaceId(event.target.value)}
              >
                <option value="">Choose workspace</option>
                {workspaces.map((workspace) => (
                  <option key={workspace.id} value={workspace.id}>
                    {workspace.name}
                  </option>
                ))}
              </select>
              <input
                className="block w-full text-sm text-muted file:mr-3 file:h-10 file:rounded-md file:border-0 file:bg-brand file:px-3 file:text-sm file:font-medium file:text-white"
                type="file"
                accept=".pdf,.docx,.txt,.csv,.md"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              />
              <Button className="w-full" disabled={isBusy || !workspaceId || !file} icon={<FileUp size={16} />}>
                Upload
              </Button>
            </form>
          </Card>
          {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}
        </div>

        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] border-collapse text-left text-sm">
              <thead className="bg-panel text-muted">
                <tr>
                  <th className="px-4 py-3 font-medium">Title</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Category</th>
                  <th className="px-4 py-3 font-medium">Pages</th>
                  <th className="px-4 py-3 font-medium">Uploaded</th>
                  <th className="px-4 py-3 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {documents.map((document) => (
                  <tr key={document.id} className="border-t border-line">
                    <td className="px-4 py-3 font-medium text-ink">{document.title}</td>
                    <td className="px-4 py-3">
                      <span className="rounded-md bg-[#E6F3F1] px-2 py-1 text-xs font-medium text-brand">
                        {document.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-muted">{document.category ?? "General"}</td>
                    <td className="px-4 py-3 text-muted">{document.page_count ?? "-"}</td>
                    <td className="px-4 py-3 text-muted">{new Date(document.created_at).toLocaleDateString()}</td>
                    <td className="px-4 py-3 text-right">
                      <button className="text-muted hover:text-accent" onClick={() => remove(document.id)}>
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </section>
  );
}
