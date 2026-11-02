export type ApiResult<T> = 
    | { kind: "ok", data: T}
    | { kind: "error", message: string};