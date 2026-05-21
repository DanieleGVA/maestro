/**
 * Authentication utilities for Keycloak JWT.
 * MVP: simple token storage and validation.
 * Tokens are stored in both localStorage (for client-side access)
 * and cookies (for Next.js Edge Middleware route protection).
 */

const TOKEN_KEY = "maestro_token";
const REFRESH_KEY = "maestro_refresh";
const COOKIE_MAX_AGE = 86400; // 24 hours

function setCookie(name: string, value: string, maxAge: number): void {
  if (typeof document === "undefined") return;
  document.cookie = `${name}=${value};path=/;max-age=${maxAge};SameSite=Lax`;
}

function deleteCookie(name: string): void {
  if (typeof document === "undefined") return;
  document.cookie = `${name}=;path=/;max-age=0;SameSite=Lax`;
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setTokens(access: string, refresh: string): void {
  localStorage.setItem(TOKEN_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
  // Mirror to cookies for middleware-based route protection
  setCookie(TOKEN_KEY, access, COOKIE_MAX_AGE);
  setCookie(REFRESH_KEY, refresh, COOKIE_MAX_AGE);
}

export function clearTokens(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  deleteCookie(TOKEN_KEY);
  deleteCookie(REFRESH_KEY);
}

export function isAuthenticated(): boolean {
  const token = getToken();
  if (!token) return false;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp * 1000 > Date.now();
  } catch {
    return false;
  }
}

export function getUserFromToken(): { sub: string; username: string; roles: string[] } | null {
  const token = getToken();
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return {
      sub: payload.sub,
      username: payload.preferred_username ?? payload.sub,
      roles: payload.realm_access?.roles ?? [],
    };
  } catch {
    return null;
  }
}
