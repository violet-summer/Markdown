import { useState } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import { login } from "../../api/auth";
import type { ApiEnvelope } from "../../models/api-contract";
import { useUiLanguage } from "../../utils/ui";

type LoginResponse = {
  token: string;
  user_id: string;
  username: string;
  email: string;
};

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const language = useUiLanguage();

  const buttonBase = "inline-flex items-center justify-center rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-[12px] font-semibold transition-all duration-150 hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60";
  const buttonPrimary = "border-2 border-[var(--accent)] bg-[var(--accent)] text-[var(--button-foreground, var(--ink))] shadow-[0_8px_30px_-20px_var(--accent)] hover:brightness-105 focus:outline-none focus:ring-2 focus:ring-[var(--accent)]";
  const fieldBase = "flex flex-col gap-1.5";
  const inputBase = "rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2.5 py-2 text-[13px] text-[var(--ink)]";
  const statusText = "mt-3 text-[12px] text-[var(--accent-2)]";
  const errorText = "mt-2 text-[12px] text-[#8a2f2f]";
  const t = language === "zh" ? {
    title: "登录",
    subtitle: "使用账号进入工作台",
    identifier: "邮箱或用户名",
    password: "密码",
    login: "登录",
    signingIn: "登录中...",
    loginFailed: "登录失败。",
    noAccount: "还没有账号？",
    createOne: "注册",
  } : {
    title: "Sign in",
    subtitle: "Access your workspace",
    identifier: "Email or username",
    password: "Password",
    login: "登录",
    signingIn: "Signing in...",
    loginFailed: "Login failed.",
    noAccount: "No account?",
    createOne: "Create one",
  };
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const performLogin = async (identifier: string, password: string) => {
    setError("");
    try {
      setStatus(t.signingIn);
      const response = (await login({ identifier, password })) as ApiEnvelope<LoginResponse>;
   console.log("登录响应", response);
   console.log("写入 token", response.data.token);


      window.localStorage.setItem("auth_token", response.data.token);
      window.dispatchEvent(new Event("auth:changed"));
      const redirectTo = (location.state as { from?: string } | null)?.from ?? "/layout";
      console.log("跳转到", redirectTo);
      navigate(redirectTo);
    } catch (err) {
      setError(err instanceof Error ? err.message : t.loginFailed);
      setStatus("");
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await performLogin(identifier, password);
  };

  return (
    <section className="mt-8 grid place-items-center">
      <div className="w-full max-w-[420px] rounded-[14px] border border-[var(--border)] bg-[linear-gradient(180deg,var(--surface),var(--surface-2))] px-5 py-[18px] shadow-[0_12px_24px_-22px_var(--shadow)]">
        <div className="mb-3">
          <h2 className="m-0 mb-3 text-[16px]">{t.title}</h2>
          <p className="m-0 text-[12px] text-[var(--muted)]">{t.subtitle}</p>
        </div>
        <form className="grid gap-3" onSubmit={handleSubmit}>
          <label className={fieldBase}>
            <span>{t.identifier}</span>
            <input
              className={inputBase}
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
              autoComplete="username"
              required
            />
          </label>
          <label className={fieldBase}>
            <span>{t.password}</span>
            <input
              className={inputBase}
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </label>
          <button className={`${buttonBase} ${buttonPrimary}`} type="submit" disabled={status !== ""}>
            {t.login}
          </button>
        </form>
        {status ? <p className={statusText}>{status}</p> : null}
        {error ? <p className={errorText}>{error}</p> : null}

        <p className="mt-4 text-[12px] text-[var(--muted)]">
          {t.noAccount} <Link to="/auth/register">{t.createOne}</Link>
        </p>
      </div>
    </section>
  );
}
