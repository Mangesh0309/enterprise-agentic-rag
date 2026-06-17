import { useState } from "react";
import { AnalyticsPage } from "./features/analytics/AnalyticsPage";
import { ChatPage } from "./features/chat/ChatPage";
import { DocumentsPage } from "./features/documents/DocumentsPage";
import { AppLayout } from "./layouts/AppLayout";
import { LoginPage } from "./pages/LoginPage";
import { useAuthStore } from "./stores/auth";

type Page = "chat" | "documents" | "analytics";

export default function App() {
  const token = useAuthStore((state) => state.token);
  const [page, setPage] = useState<Page>("chat");

  if (!token) {
    return <LoginPage />;
  }

  return (
    <AppLayout page={page} onPageChange={setPage}>
      {page === "chat" ? <ChatPage /> : null}
      {page === "documents" ? <DocumentsPage /> : null}
      {page === "analytics" ? <AnalyticsPage /> : null}
    </AppLayout>
  );
}
