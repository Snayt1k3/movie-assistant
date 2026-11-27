import { useState } from "react";
import type { ChangeEvent, SubmitEvent } from "react";
import { register } from "../../api/auth";
import type { FieldErrors } from "../../api/auth";
import type { RegisterIn } from "../../api/types";
import { fieldErrorLabel, fieldLabels } from "./labels";
import { RegisterSchema, toFieldErrors } from "./schema";

type Status =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "invalid"; fields: FieldErrors }
  | { kind: "failed"; message: string }
  | { kind: "done" };

const empty: RegisterIn = { email: "", password: "", display_name: "" };

export function RegisterForm() {
  const [values, setValues] = useState<RegisterIn>(empty);
  const [status, setStatus] = useState<Status>({ kind: "idle" });

  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.currentTarget;
    setValues((prev) => ({ ...prev, [name]: value }));
  }
  async function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
    e.preventDefault();

    const parsed = RegisterSchema.safeParse(values);
    if (!parsed.success) {
      setStatus({ kind: "invalid", fields: toFieldErrors(parsed.error) });
      return; // на сервер не идём
    }

    setStatus({ kind: "submitting" });
    const r = await register(parsed.data); // values или parsed.data — что отправлять?

    switch (r.kind) {
      case "ok":
        setStatus({ kind: "done" });
        return;
      case "invalid":
        setStatus({ kind: "invalid", fields: r.fields });
        return;
      case "unavailable":
        setStatus({ kind: "failed", message: r.message });
        return;
      default: {
        const _exhaustive: never = r;
        return _exhaustive;
      }
    }
  }

  if (status.kind === "done") return <p>Готово, вы вошли.</p>;

  // ошибки полей есть только в статусе "invalid"; в остальных — пустой объект
  const errors: FieldErrors = status.kind === "invalid" ? status.fields : {};

  return (
    <form onSubmit={handleSubmit} noValidate>
      <div>
        <label>
          {fieldLabels.email}
          <input
            name="email"
            type="email"
            autoComplete="email"
            value={values.email}
            onChange={handleChange}
          />
        </label>
        {errors.email !== undefined && <p>{fieldErrorLabel("email", errors.email)}</p>}
      </div>

      <div>
        <label>
          {fieldLabels.display_name}
          <input
            name="display_name"
            type="text"
            autoComplete="nickname"
            value={values.display_name}
            onChange={handleChange}
          />
        </label>
        {errors.display_name !== undefined && (
          <p>{fieldErrorLabel("display_name", errors.display_name)}</p>
        )}
      </div>

      <div>
        <label>
          {fieldLabels.password}
          <input
            name="password"
            type="password"
            autoComplete="new-password"
            value={values.password}
            onChange={handleChange}
          />
        </label>
        {errors.password !== undefined && <p>{fieldErrorLabel("password", errors.password)}</p>}
      </div>

      {status.kind === "failed" && <p>Не удалось зарегистрироваться: {status.message}</p>}

      <button type="submit" disabled={status.kind === "submitting"}>
        Зарегистрироваться
      </button>
    </form>
  );
}
