import { useState } from "react";
import { API_BASE_URL } from "../api/client";
import { useAuthStore } from "../stores/auth";
import type { ChatResponse } from "../types";

interface StreamPayload {
  query: string;
  workspace_id?: string | null;
  conversation_id?: string | null;
  use_web: boolean;
}

export function useStreamChat() {
  const [isStreaming, setIsStreaming] = useState(false);
  const token = useAuthStore((state) => state.token);

  async function streamChat(
    payload: StreamPayload,
    onToken: (token: string) => void,
    onDone: (response: ChatResponse) => void,
  ) {
    setIsStreaming(true);
    try {
      const response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok || !response.body) {
        throw new Error("Unable to start chat stream");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";

        for (const event of events) {
          const eventName = event.match(/^event: (.+)$/m)?.[1];
          const data = event.match(/^data: (.+)$/m)?.[1];
          if (!eventName || !data) continue;
          const parsed = JSON.parse(data);
          if (eventName === "token") onToken(parsed.token);
          if (eventName === "done") onDone(parsed as ChatResponse);
          if (eventName === "error") throw new Error(parsed.detail);
        }
      }
    } finally {
      setIsStreaming(false);
    }
  }

  return { isStreaming, streamChat };
}
