import { z } from "zod";
import { isRegisterField } from "../../api/auth";
import type { FieldErrors } from "../../api/auth";
import type { LoginIn, RegisterIn } from "../../api/types";

// message = код ошибки (как type у Pydantic), текст подставит labels.ts
export const RegisterSchema = z.object({
  email: z.string().trim().pipe(z.email("value_error")),
  password: z.string().min(8, "string_too_short").max(128, "string_too_long"), // 8–128 символов, коды "string_too_short" / "string_too_long"
  display_name: z.string().trim().min(1, "string_too_short").max(64, "string_too_long"), // trim, затем 1–64
}) satisfies z.ZodType<RegisterIn>;

// ZodError → FieldErrors; по смыслу то же, что parseValidation в api/auth.ts
export function toFieldErrors(error: z.ZodError): FieldErrors {
  const fields: FieldErrors = {};
  for (const issue of error.issues) {
    const field = issue.path[0]; // где у issue имя поля? (подсказка: issue.path — массив, как loc)
    if (isRegisterField(field)) {
      fields[field] ??= issue.message;
    }
  }
  return fields;
}

export const LoginSchema = z.object({
  email: z.string().trim().pipe(z.email("value_error")),
  password: z.string().min(1, "missing"),
}) satisfies z.ZodType<LoginIn>;
