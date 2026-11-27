import type { ApiResult } from "./result";

export async function getJson(url: string): Promise<ApiResult<unknown>> {
  try {
    const res = await fetch(url);
    if (!res.ok) {
      return {kind: "error", message: `HTTP ${res.status}`} 
    }
    const data: unknown = await res.json();
    return {kind: "ok", data}
  } catch (e) {
    let err: string

    if (e instanceof Error) {err = e.message} else {err = "network error"}

    return {kind: "error", message: err}
  }
}

export type RawResponse =
  | { kind: "ok"; status: number; data: unknown }
  | { kind: "http_error"; status: number; body: unknown }
  | { kind: "network_error"; message: string };

type Method = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export async function request(
  method: Method,
  url: string,
  body?: unknown, // тело запроса; `?:` — чтобы GET вызывался без третьего аргумента
): Promise<RawResponse> {
  let res: Response;

  try {
    res = await fetch(url, {
      method,
      headers: body !== undefined ? { "Content-Type": "application/json" } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch (e) {
    return {
      kind: "network_error",
      message: e instanceof Error ? e.message : "network error",
    };
  }

  // 204 (например, /auth/logout) приходит с пустым телом — res.json() на нём бросит.
  // Не-JSON (HTML от прокси при упавшем бэкенде) считаем недоступностью сервера, а не ответом API.
  let data: unknown;
  try {
    data = res.status !== 204 ? await res.json() : null;
  } catch {
    return { kind: "network_error", message: `non-JSON response (HTTP ${res.status})` };
  }

  if (!res.ok) {
    return { kind: "http_error", status: res.status, body: data };
  }
  return { kind: "ok", status: res.status, data };
}