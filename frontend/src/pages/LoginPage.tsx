import { FormEvent, useState } from "react";
import { Lock, UserPlus } from "lucide-react";
import { apiFetch } from "../api/client";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { useAuthStore } from "../stores/auth";
import type { User } from "../types";

export function LoginPage() {
  const setSession = useAuthStore((state) => state.setSession);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("admin@example.com");
  const [fullName, setFullName] = useState("Platform Admin");
  const [password, setPassword] = useState("enterprise-rag");
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      if (mode === "register") {
        await apiFetch<User>("/auth/register", {
          auth: false,
          method: "POST",
          body: JSON.stringify({ email, full_name: fullName, password }),
        });
      }

      const form = new URLSearchParams();
      form.set("username", email);
      form.set("password", password);
      const token = await apiFetch<{ access_token: string; user: User }>("/auth/login", {
        auth: false,
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form,
      });
      setSession(token.access_token, token.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-panel px-4">
      <Card className="w-full max-w-md p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold text-ink">Enterprise RAG</h1>
          <p className="mt-2 text-sm text-muted">Sign in to continue.</p>
        </div>
        <form className="space-y-4" onSubmit={submit}>
          {mode === "register" ? (
            <label className="block">
              <span className="text-sm font-medium text-ink">Full name</span>
              <input
                className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-brand"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
              />
            </label>
          ) : null}
          <label className="block">
            <span className="text-sm font-medium text-ink">Email</span>
            <input
              className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-brand"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              type="email"
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-ink">Password</span>
            <input
              className="mt-1 h-11 w-full rounded-md border border-line px-3 outline-none focus:border-brand"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
            />
          </label>
          {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}
          <Button className="w-full" icon={mode === "login" ? <Lock size={16} /> : <UserPlus size={16} />}>
            {mode === "login" ? "Sign in" : "Create account"}
          </Button>
        </form>
        <button
          className="mt-4 w-full text-sm font-medium text-brand hover:text-[#19665B]"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
        >
          {mode === "login" ? "Create the first account" : "Use an existing account"}
        </button>
      </Card>
    </main>
  );
}
