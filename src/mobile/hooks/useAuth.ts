/**
 * MAESTRO auth hook.
 *
 * Manages login, logout, auto-refresh of JWT tokens.
 * Auth state is derived from secure-stored tokens (no PII in memory beyond tokens).
 */

import { useState, useEffect, useCallback } from 'react';
import {
  login as authLogin,
  logout as authLogout,
  isAuthenticated as checkAuth,
  refreshAccessToken,
  getTokens,
} from '../services/auth';
import type { LoginCredentials } from '../types';

interface UseAuthReturn {
  isLoggedIn: boolean;
  isLoading: boolean;
  loginError: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
}

export function useAuth(): UseAuthReturn {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [loginError, setLoginError] = useState<string | null>(null);

  // Check auth state on mount
  useEffect(() => {
    (async () => {
      const authed = await checkAuth();
      if (!authed) {
        // Try refresh
        const refreshed = await refreshAccessToken();
        setIsLoggedIn(refreshed !== null);
      } else {
        setIsLoggedIn(true);
      }
      setIsLoading(false);
    })();
  }, []);

  // Auto-refresh token before expiry
  useEffect(() => {
    if (!isLoggedIn) return;

    const interval = setInterval(async () => {
      const tokens = await getTokens();
      if (!tokens) return;
      // Refresh 5 minutes before expiry
      const fiveMinutes = 5 * 60 * 1000;
      if (tokens.expiresAt - Date.now() < fiveMinutes) {
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
          setIsLoggedIn(false);
        }
      }
    }, 60000);

    return () => clearInterval(interval);
  }, [isLoggedIn]);

  const login = useCallback(async (credentials: LoginCredentials) => {
    setLoginError(null);
    setIsLoading(true);
    try {
      await authLogin(credentials);
      setIsLoggedIn(true);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Credenziali non valide. Riprova.';
      setLoginError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    await authLogout();
    setIsLoggedIn(false);
  }, []);

  return { isLoggedIn, isLoading, loginError, login, logout };
}
