import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import client, { storeTokens, clearTokens } from "../api/client";

interface User {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
}

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await client.get("/users/me/");
        setUser(res.data);
      } catch {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  async function login(email: string, password: string) {
    const res = await client.post("/login/", { email, password });
    const { access, refresh } = res.data;
    await storeTokens(access, refresh);
    setToken(access);
    const meRes = await client.get("/users/me/");
    setUser(meRes.data);
  }

  async function logout() {
    try {
      await client.post("/logout/", {});
    } catch {}
    await clearTokens();
    setUser(null);
    setToken(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
