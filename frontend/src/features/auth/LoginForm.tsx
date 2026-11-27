import { useState } from "react";
import type { ChangeEvent, SubmitEvent } from "react";
import { login } from "../../api/auth";
import type { FieldErrors } from "../../api/auth";
import type { LoginIn } from "../../api/types";
import { fieldErrorLabel, fieldLabels } from "./labels";
import { LoginSchema, toFieldErrors } from "./schema";

type Status =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "invalid"; fields: FieldErrors }
  | { kind: "bad_credentials" }
  | { kind: "failed"; message: string }
  | { kind: "done" };

const empty: LoginIn = { email: "", password: "" };

export function LoginForm() {
  const [values, setValues] = useState<LoginIn>(empty);
  const [status, setStatus] = useState<Status>({ kind: "idle" });

  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.currentTarget;
    setValues((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
    e.preventDefault();

    const parsed = LoginSchema.safeParse(values);
    if (!parsed.success) {
      setStatus({ kind: "invalid", fields: toFieldErrors(parsed.error) });
      return; // на сервер не идём
    }

    setStatus({ kind: "submitting" });
    const r = await login(parsed.data);

    switch (r.kind) {
      case "ok":
        setStatus({ kind: "done" });
        return;
      case "bad_credentials":
        setStatus({ kind: "bad_credentials" });
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

  const errors: FieldErrors = status.kind === "invalid" ? status.fields : {};

  return (
    <form onSubmit={handleSubmit} noValidate>
      {/* 401 не привязан к полю: сервер не говорит, что именно неверно (защита от перебора email) */}
      {status.kind === "bad_credentials" && <p>Неверный email или пароль</p>}

      <div>
        <label>
          {fieldLabels.email}
          <input name="email" type="email" autoComplete="email"
                 value={values.email} onChange={handleChange} />
        </label>
        {errors.email !== undefined && <p>{fieldErrorLabel("email", errors.email)}</p>}
      </div>

      <div>
        <label>
          {fieldLabels.password}
          <input name="password" type="password" autoComplete="current-password"
                 value={values.password} onChange={handleChange} />
        </label>
        {errors.password !== undefined && <p>{fieldErrorLabel("password", errors.password)}</p>}
      </div>

      {status.kind === "failed" && <p>Не удалось войти: {status.message}</p>}

      <button type="submit" disabled={status.kind === "submitting"}>Войти</button>
    </form>
  );
}
