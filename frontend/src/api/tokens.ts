import type { TokenPair } from "./types";

const REFRESH_KEY = "seans.refresh_token";

let access: { token: string; expiresAtMs: number } | null = null;

export function setTokens(pair: TokenPair): void {
  access = {
    token: pair.access_token,
    expiresAtMs: Date.now() + pair.expires_in * 1000,
  };
  try {
    localStorage.setItem(REFRESH_KEY, pair.refresh_token);
  } catch {
    // не удалось — сессия просто не переживёт перезагрузку
  }
}

export function getAccessToken(): string | null {
  if (access !== null && Date.now() < access.expiresAtMs - 30_000) {
    return access.token;
  }
  return null;
}

export function getRefreshToken(): string | null {
  try {
    return localStorage.getItem(REFRESH_KEY);
  } catch {
    return null;
  }
}

export function clearTokens(): void {
  access = null;
  try {
    localStorage.removeItem(REFRESH_KEY);
  } catch {
    // хранилище недоступно — значит, и токена там нет
  }
}