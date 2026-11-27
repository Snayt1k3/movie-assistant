import type { RegisterField } from "../../api/auth";

export const fieldLabels: Record<RegisterField, string> = {
  email: "Email",
  password: "Пароль",
  display_name: "Имя",
};

// code — то, что лежит в FieldErrors: "missing", "string_too_short", "value_error", "email_taken"
export function fieldErrorLabel(field: RegisterField, code: string): string {
  if (code === "email_taken") return "Этот email уже зарегистрирован";
  if (code === "missing") return "Обязательное поле";
  if (code === "value_error" && field === "email") return "Некорректный email";
  if (code === "string_too_short") {
    if (field === "password") return "Минимум 8 символов";
    if (field === "display_name") return "Введите имя";
  }
  return "Проверьте это поле"; // незнакомый код — не падаем, показываем общий текст
}
