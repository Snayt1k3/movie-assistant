import { LoginForm } from "./features/auth/LoginForm";
import { RegisterForm } from "./features/auth/RegisterForm";

// Роутера пока нет — обе формы на одной странице.
export default function App() {
  return (
    <>
      <LoginForm />
      <hr />
      <RegisterForm />
    </>
  );
}
