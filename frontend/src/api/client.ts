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