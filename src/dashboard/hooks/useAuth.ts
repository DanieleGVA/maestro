"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { clearTokens, getUserFromToken, isAuthenticated, setTokens } from "@/lib/auth";
import api from "@/lib/api";

interface AuthUser {
  sub: string;
  username: string;
  roles: string[];
}

export function useAuth() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isAuthenticated()) {
      setUser(getUserFromToken());
    }
    setLoading(false);
  }, []);

  const login = useCallback(
    async (username: string, password: string) => {
      const res = await api.post("/api/v1/auth/login", { username, password });
      setTokens(res.data.access_token, res.data.refresh_token);
      const u = getUserFromToken();
      setUser(u);
      // Redirect to the originally requested page, or home
      const params = new URLSearchParams(window.location.search);
      const redirectTo = params.get("redirect") ?? "/";
      router.push(redirectTo);
    },
    [router],
  );

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
    router.push("/login");
  }, [router]);

  return { user, loading, login, logout, isAuthenticated: !!user };
}
