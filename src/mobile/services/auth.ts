/**
 * MAESTRO auth service -- Keycloak token management.
 *
 * MVP: username + password login via Keycloak token endpoint.
 * Tokens stored in expo-secure-store (encrypted, not in plain AsyncStorage).
 * JWT expiry: 1h access, 24h refresh (per phase3-compliance-mvp.md T3.5).
 *
 * No PII is logged or stored outside secure storage.
 */

import * as SecureStore from 'expo-secure-store';
import axios from 'axios';
import type { AuthTokens, LoginCredentials } from '../types';

const KEYCLOAK_URL = process.env.EXPO_PUBLIC_KEYCLOAK_URL ?? 'http://localhost:8080';
const KEYCLOAK_REALM = process.env.EXPO_PUBLIC_KEYCLOAK_REALM ?? 'maestro';
const KEYCLOAK_CLIENT_ID = process.env.EXPO_PUBLIC_KEYCLOAK_CLIENT_ID ?? 'maestro-student';

const TOKEN_KEY = 'maestro_auth_tokens';

/**
 * Login with username/password via Keycloak Resource Owner Password Grant.
 */
export async function login(credentials: LoginCredentials): Promise<AuthTokens> {
  const tokenUrl = `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/token`;

  const params = new URLSearchParams({
    grant_type: 'password',
    client_id: KEYCLOAK_CLIENT_ID,
    username: credentials.username,
    password: credentials.password,
  });

  const response = await axios.post(tokenUrl, params.toString(), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  const tokens: AuthTokens = {
    accessToken: response.data.access_token,
    refreshToken: response.data.refresh_token,
    expiresAt: Date.now() + response.data.expires_in * 1000,
  };

  await storeTokens(tokens);
  return tokens;
}

/**
 * Refresh the access token using the refresh token.
 */
export async function refreshAccessToken(): Promise<AuthTokens | null> {
  const current = await getTokens();
  if (!current?.refreshToken) return null;

  const tokenUrl = `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/token`;

  const params = new URLSearchParams({
    grant_type: 'refresh_token',
    client_id: KEYCLOAK_CLIENT_ID,
    refresh_token: current.refreshToken,
  });

  try {
    const response = await axios.post(tokenUrl, params.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    const tokens: AuthTokens = {
      accessToken: response.data.access_token,
      refreshToken: response.data.refresh_token,
      expiresAt: Date.now() + response.data.expires_in * 1000,
    };

    await storeTokens(tokens);
    return tokens;
  } catch {
    await clearTokens();
    return null;
  }
}

/**
 * Logout: clear stored tokens.
 */
export async function logout(): Promise<void> {
  await clearTokens();
}

/**
 * Read stored tokens from secure storage.
 */
export async function getTokens(): Promise<AuthTokens | null> {
  const raw = await SecureStore.getItemAsync(TOKEN_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthTokens;
  } catch {
    return null;
  }
}

/**
 * Check whether a valid (non-expired) token exists.
 */
export async function isAuthenticated(): Promise<boolean> {
  const tokens = await getTokens();
  if (!tokens) return false;
  // Allow 30s buffer before expiry
  return tokens.expiresAt > Date.now() + 30000;
}

// --- Internal helpers ---

async function storeTokens(tokens: AuthTokens): Promise<void> {
  await SecureStore.setItemAsync(TOKEN_KEY, JSON.stringify(tokens));
}

async function clearTokens(): Promise<void> {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
}
