import type { RegisterField } from "../../api/auth";

export const fieldLabels: Record<RegisterField, string> = {
  email: "Email",
  password: "Password",
  display_name: "DisplayName",
};

// code — то, что лежит в FieldErrors: "missing", "string_too_short", "value_error", "email_taken"
export function fieldErrorLabel(field: RegisterField, code: string): string {
  if (code === "email_taken") return "Этот email уже зарегистрирован";
  if (code === "missing") return "Обязательное поле";
  if (code === "value_error" && field === "email") return "Email введен некоректно";
  if (code === "string_too_short") {
    // для password — «минимум 8 символов», для display_name — «введите имя»
    if (field === "password") return "минимум 8 символов"
    if (field === "display_name") return "введите имя"
   }
  return "Проверьте это поле"; // незнакомый код — не падаем, показываем общий текст
}