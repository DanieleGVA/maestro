"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";

/**
 * Teacher login page.
 * Keyboard flow: Tab -> username -> password -> submit (accessibility-mvp-spec.md Section 5.1.1).
 */
export default function LoginPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
    } catch {
      setError("Credenziali non valide. Riprova.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-bg">
      <div className="w-full max-w-sm rounded-lg bg-white p-8 shadow-lg">
        <h1 className="mb-6 text-center text-2xl font-bold text-page-fg">
          MAESTRO
        </h1>
        <p className="mb-6 text-center text-sm text-surface-fg">
          Accedi alla Dashboard Docente
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div role="alert" className="rounded-md bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="username" className="mb-1 block text-sm font-medium text-page-fg">
              Nome utente
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
              className="w-full rounded-md border border-border-input px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium text-page-fg">
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
                className="w-full rounded-md border border-border-input px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
              />
            </div>
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="mt-1 text-xs text-surface-fg hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
            >
              {showPassword ? "Nascondi password" : "Mostra password"}
            </button>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-focus px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus"
          >
            {loading ? "Accesso in corso..." : "Accedi"}
          </button>
        </form>
      </div>
    </div>
  );
}
