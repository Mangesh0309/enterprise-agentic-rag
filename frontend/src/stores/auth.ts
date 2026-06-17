import { create } from "zustand";
import type { User } from "../types";

interface AuthState {
  token: string | null;
  user: User | null;
  setSession: (token: string, user: User) => void;
  clearSession: () => void;
}

const storedToken = localStorage.getItem("rag.token");
const storedUser = localStorage.getItem("rag.user");

export const useAuthStore = create<AuthState>((set) => ({
  token: storedToken,
  user: storedUser ? (JSON.parse(storedUser) as User) : null,
  setSession: (token, user) => {
    localStorage.setItem("rag.token", token);
    localStorage.setItem("rag.user", JSON.stringify(user));
    set({ token, user });
  },
  clearSession: () => {
    localStorage.removeItem("rag.token");
    localStorage.removeItem("rag.user");
    set({ token: null, user: null });
  },
}));
