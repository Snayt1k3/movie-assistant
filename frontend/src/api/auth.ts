import { z } from "zod";
import { request } from "./client";
import { clearTokens, setTokens, getRefreshToken } from "./tokens";
import type { TokenPair, RegisterIn, LoginIn } from "./types";


const TokenPairSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string(),
  expires_in: z.number(),
}) satisfies z.ZodType<TokenPair>;

// ─── refresh ───

export type RefreshResult =
  | { kind: "ok"; accessToken: string }
  | { kind: "unauthorized" }
  | { kind: "unavailable"; message: string };

async function doRefresh(): Promise<RefreshResult> {
  const token = getRefreshToken();
  if (token === null) return { kind: "unauthorized" };

  const r = await request("POST", "/api/v1/auth/refresh", { refresh_token: token });

  switch (r.kind) {
    case "network_error":
      return { kind: "unavailable", message: r.message };
    case "http_error":
      if (r.status === 401) {
        clearTokens();
        return { kind: "unauthorized" };
      }
      return { kind: "unavailable", message: `HTTP ${r.status}` };
    case "ok": {
      const parsed = TokenPairSchema.safeParse(r.data);
      if (!parsed.success) {
        // старый refresh уже сожжён ротацией — сессию не спасти
        console.error(parsed.error);
        clearTokens();
        return { kind: "unauthorized" };
      }
      setTokens(parsed.data);
      return { kind: "ok", accessToken: parsed.data.access_token };
    }
    default: {
      const _exhaustive: never = r;
      return _exhaustive;
    }
  }
}

// Single-flight: одновременные вызовы получают один и тот же промис.
let inflight: Promise<RefreshResult> | null = null;

export function refresh(): Promise<RefreshResult> {
  if (inflight !== null) return inflight;
  inflight = doRefresh().finally(() => {
    inflight = null;
  });
  return inflight;
}

// ─── register ───

export type RegisterField = keyof RegisterIn;

export function isRegisterField(x: unknown): x is RegisterField {
  return x === "email" || x === "password" || x === "display_name";
}

// Значения — коды ошибок (type из Pydantic или свой "email_taken"), тексты подставляет UI.
export type FieldErrors = Partial<Record<RegisterField, string>>;

export type RegisterResult =
  | { kind: "ok" }
  | { kind: "invalid"; fields: FieldErrors }
  | { kind: "unavailable"; message: string };

const ValidationErrorSchema = z.object({
  detail: z.array(
    z.object({
      type: z.string(),
      loc: z.array(z.union([z.string(), z.number()])),
    }),
  ),
});

export async function register(body: RegisterIn): Promise<RegisterResult> {
  const r = await request("POST", "/api/v1/auth/register", body);

  switch (r.kind) {
    case "network_error":
      return { kind: "unavailable", message: r.message };
    case "ok": {
      return storeTokens(r.data) ? { kind: "ok" } : { kind: "unavailable", message: "bad token response" };
    }
    case "http_error":
      if (r.status === 409) return { kind: "invalid", fields: { email: "email_taken" } };
      if (r.status === 422) return parseValidation(r.body);
      return { kind: "unavailable", message: `HTTP ${r.status}` };
    default: {
      const _exhaustive: never = r;
      return _exhaustive;
    }
  }
}

function parseValidation(body: unknown): RegisterResult {
  const parsed = ValidationErrorSchema.safeParse(body);
  if (!parsed.success) {
    console.error(parsed.error);
    return { kind: "unavailable", message: parsed.error.message };
  }

  const fields: FieldErrors = {};
  for (const item of parsed.data.detail) {
    const field = item.loc[1]; // loc = ["body", "password"]
    if (isRegisterField(field)) {
      fields[field] ??= item.type;
    }
  }

  return { kind: "invalid", fields };
}

// true — токены сохранены; false — ответ не прошёл схему (залогировано)
function storeTokens(data: unknown): boolean {
  const parsed = TokenPairSchema.safeParse(data);
  if (!parsed.success) {
    console.error(parsed.error);
    return false;
  }
  setTokens(parsed.data);
  return true;
}

// ─── login ───

export type LoginResult =
  | { kind: "ok" }
  | { kind: "bad_credentials" }
  | { kind: "unavailable"; message: string };

export async function login(body: LoginIn): Promise<LoginResult> {
  const r = await request("POST", "/api/v1/auth/login", body);
  switch (r.kind) {
    case "network_error":
      return { kind: "unavailable", message: r.message };
    case "ok":
      return storeTokens(r.data) ? { kind: "ok" } : { kind: "unavailable", message: "bad token response" };
    case "http_error":
      if (r.status === 401) return {kind: "bad_credentials"};
      return { kind: "unavailable", message: `HTTP ${r.status}` };
    default: {
      const _exhaustive: never = r;
      return _exhaustive;
    }
  }
}