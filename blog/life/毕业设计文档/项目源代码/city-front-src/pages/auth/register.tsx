import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {register, RegisterResponse} from "@/api/auth";
import type { ApiEnvelope } from "@/models/api-contract";
import { useUiLanguage } from "@/utils/ui";


export function RegisterPage() {
  const navigate = useNavigate();
  const language = useUiLanguage();
  const t = language === "zh" ? {
    title: "创建账号",
    subtitle: "注册后可保存布局与模型",
    user_name: "用户名",
    email: "邮箱",
    password: "密码",
    register: "注册",
    creating: "创建账号中...",
    failed: "注册失败。",
    haveAccount: "已有账号？",
    signIn: "登录",
  } : {
    title: "Create account",
    subtitle: "Save layouts and models after sign up",
    user_name: "user_name",
    email: "Email",
    password: "Password",
    register: "注册",
    creating: "Creating account...",
    failed: "Registration failed.",
    haveAccount: "Already have an account?",
    signIn: "Sign in",
  };
  const [user_name, setuser_name] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState("");
  const buttonBase = "inline-flex items-center justify-center rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-[12px] font-semibold transition-all duration-150 hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-16px_var(--shadow)] disabled:cursor-not-allowed disabled:opacity-60";
  const buttonPrimary = "border-transparent bg-[var(--accent)]  text-[var(--button-foreground, var(--ink))]";
  const fieldBase = "flex flex-col gap-1.5";
  const inputBase = "rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2.5 py-2 text-[13px] text-[var(--ink)]";
  const statusText = "mt-3 text-[12px] text-[var(--accent-2)]";
  const errorText = "mt-2 text-[12px] text-[#8a2f2f]";
  const [error, setError] = useState("");

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");

    try {
      setStatus(t.creating);
      const response = (await register({ user_name, email, password })) as ApiEnvelope<RegisterResponse>;
      window.localStorage.setItem("auth_token", response.data.token);
      window.dispatchEvent(new Event("auth:changed"));
      navigate("/layout");
    } catch (err) {
      setError(err instanceof Error ? err.message : t.failed);
    } finally {
      setStatus("");
    }
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
            <span>{t.user_name}</span>
            <input
              className={inputBase}
              value={user_name}
              onChange={(event) => setuser_name(event.target.value)}
              autoComplete="user_name"
              required
            />
          </label>
          <label className={fieldBase}>
            <span>{t.email}</span>
            <input
              className={inputBase}
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
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
              autoComplete="new-password"
              required
            />
          </label>
          <button className={`${buttonBase} ${buttonPrimary}`} type="submit">
            {t.register}
          </button>
        </form>
        {status ? <p className={statusText}>{status}</p> : null}
        {error ? <p className={errorText}>{error}</p> : null}
        <p className="mt-4 text-[12px] text-[var(--muted)]">
          {t.haveAccount} <Link to="/auth/login">{t.signIn}</Link>
        </p>
      </div>
    </section>
  );
}
