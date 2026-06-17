import { BarChart3, Bot, FileStack, LogOut } from "lucide-react";
import type { ReactNode } from "react";
import { Button } from "../components/Button";
import { useAuthStore } from "../stores/auth";

type Page = "chat" | "documents" | "analytics";

interface AppLayoutProps {
  page: Page;
  onPageChange: (page: Page) => void;
  children: ReactNode;
}

const navItems = [
  { id: "chat" as const, label: "Chat", icon: Bot },
  { id: "documents" as const, label: "Documents", icon: FileStack },
  { id: "analytics" as const, label: "Analytics", icon: BarChart3 },
];

export function AppLayout({ page, onPageChange, children }: AppLayoutProps) {
  const { user, clearSession } = useAuthStore();

  return (
    <div className="flex min-h-screen bg-panel">
      <aside className="hidden w-64 border-r border-line bg-white p-4 md:flex md:flex-col">
        <div className="mb-8">
          <div className="text-lg font-semibold text-ink">Enterprise RAG</div>
          <div className="mt-1 text-sm text-muted">{user?.full_name}</div>
        </div>
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={`flex h-10 w-full items-center gap-3 rounded-md px-3 text-sm font-medium ${
                  page === item.id ? "bg-[#E6F3F1] text-brand" : "text-muted hover:bg-panel hover:text-ink"
                }`}
                onClick={() => onPageChange(item.id)}
              >
                <Icon size={18} />
                {item.label}
              </button>
            );
          })}
        </nav>
        <Button
          className="mt-auto w-full"
          variant="secondary"
          icon={<LogOut size={16} />}
          onClick={clearSession}
        >
          Sign out
        </Button>
      </aside>
      <main className="min-w-0 flex-1">{children}</main>
    </div>
  );
}
