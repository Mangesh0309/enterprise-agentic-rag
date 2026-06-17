import { FormEvent, useEffect, useMemo, useState } from "react";
import { CheckCircle2, Send, ThumbsDown, ThumbsUp } from "lucide-react";
import { apiFetch } from "../../api/client";
import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import { CitationList } from "../../components/CitationList";
import { useStreamChat } from "../../hooks/useStreamChat";
import type { ChatResponse, Citation, Workspace } from "../../types";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  confidence?: number;
  messageId?: string;
}

export function ChatPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [workspaceId, setWorkspaceId] = useState<string>("");
  const [query, setQuery] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const { isStreaming, streamChat } = useStreamChat();

  useEffect(() => {
    apiFetch<Workspace[]>("/workspaces").then(setWorkspaces).catch(() => setWorkspaces([]));
  }, []);

  const activeWorkspace = useMemo(
    () => workspaces.find((workspace) => workspace.id === workspaceId),
    [workspaceId, workspaces],
  );

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!query.trim() || isStreaming) return;
    const userText = query.trim();
    setQuery("");
    setError(null);
    setMessages((current) => [...current, { role: "user", content: userText }, { role: "assistant", content: "" }]);

    try {
      await streamChat(
        {
          query: userText,
          workspace_id: workspaceId || null,
          conversation_id: conversationId,
          use_web: true,
        },
        (token) => {
          setMessages((current) => {
            const next = [...current];
            const last = next[next.length - 1];
            next[next.length - 1] = { ...last, content: `${last.content}${token}` };
            return next;
          });
        },
        (response: ChatResponse) => {
          setConversationId(response.conversation_id);
          setMessages((current) => {
            const next = [...current];
            next[next.length - 1] = {
              role: "assistant",
              content: response.answer,
              citations: response.citations,
              confidence: response.confidence_score,
              messageId: response.message_id,
            };
            return next;
          });
        },
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat failed");
    }
  }

  async function rate(messageId: string, rating: number) {
    await apiFetch("/feedback", {
      method: "POST",
      body: JSON.stringify({ message_id: messageId, rating }),
    });
  }

  return (
    <section className="flex h-screen flex-col">
      <header className="border-b border-line bg-white px-4 py-3 md:px-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-ink">Knowledge Assistant</h2>
            <div className="mt-1 flex items-center gap-2 text-sm text-muted">
              <CheckCircle2 size={16} className="text-brand" />
              {activeWorkspace?.name ?? "Web and assigned workspaces"}
            </div>
          </div>
          <select
            className="h-10 rounded-md border border-line bg-white px-3 text-sm outline-none focus:border-brand"
            value={workspaceId}
            onChange={(event) => setWorkspaceId(event.target.value)}
          >
            <option value="">All accessible knowledge</option>
            {workspaces.map((workspace) => (
              <option key={workspace.id} value={workspace.id}>
                {workspace.name}
              </option>
            ))}
          </select>
        </div>
      </header>

      <div className="scrollbar-thin flex-1 overflow-y-auto px-4 py-5 md:px-6">
        <div className="mx-auto max-w-5xl space-y-4">
          {messages.length === 0 ? (
            <Card className="p-5">
              <h3 className="text-lg font-semibold text-ink">Ask a question</h3>
              <p className="mt-2 text-sm leading-6 text-muted">
                Answers use internal retrieval, Tavily search when current context is needed, verification, and citations.
              </p>
            </Card>
          ) : null}
          {messages.map((message, index) => (
            <div key={index} className={message.role === "user" ? "flex justify-end" : "flex justify-start"}>
              <div
                className={`max-w-[880px] rounded-lg px-4 py-3 ${
                  message.role === "user" ? "bg-brand text-white" : "border border-line bg-white text-ink"
                }`}
              >
                <div className="whitespace-pre-wrap text-sm leading-6">{message.content}</div>
                {message.role === "assistant" && message.confidence !== undefined ? (
                  <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-muted">
                    <span>{Math.round(message.confidence * 100)}% confidence</span>
                    {message.messageId ? (
                      <>
                        <button className="hover:text-brand" onClick={() => rate(message.messageId!, 5)}>
                          <ThumbsUp size={16} />
                        </button>
                        <button className="hover:text-accent" onClick={() => rate(message.messageId!, 1)}>
                          <ThumbsDown size={16} />
                        </button>
                      </>
                    ) : null}
                  </div>
                ) : null}
                {message.citations ? <div className="mt-3"><CitationList citations={message.citations} /></div> : null}
              </div>
            </div>
          ))}
          {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}
        </div>
      </div>

      <form className="border-t border-line bg-white p-4 md:px-6" onSubmit={submit}>
        <div className="mx-auto flex max-w-5xl gap-3">
          <textarea
            className="min-h-12 flex-1 resize-none rounded-md border border-line px-3 py-3 text-sm outline-none focus:border-brand"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Ask about policy, reports, systems, decisions, or current context"
          />
          <Button className="h-12 px-4" disabled={isStreaming} icon={<Send size={16} />}>
            Send
          </Button>
        </div>
      </form>
    </section>
  );
}
