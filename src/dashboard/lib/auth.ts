/**
 * Authentication utilities for Keycloak JWT.
 * MVP: simple token storage and validation.
 */

const TOKEN_KEY = "maestro_token";
const REFRESH_KEY = "maestro_refresh";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setTokens(access: string, refresh: string): void {
  localStorage.setItem(TOKEN_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
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
