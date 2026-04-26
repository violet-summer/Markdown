import { useEffect, useState } from "react";
import { getMe, updateMe } from "../api/user";
import type { ApiEnvelope } from "../models/api-contract";
import { useUiLanguage } from "../utils/ui";

type UserProfile = {
  userId: string;
  username: string;
  email: string;
};

export function ProfilePage() {
  const language = useUiLanguage();
  const buttonBase = "inline-flex items-center justify-center rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-[12px] font-semibold transition-all duration-150 hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-16px_var(--shadow)]";
  const buttonPrimary = "border-transparent bg-[var(--accent)] text-white";
  const fieldBase = "flex flex-col gap-1.5";
  const inputBase = "rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2.5 py-2 text-[13px] text-[var(--ink)]";
  const statusText = "mt-3 text-[12px] text-[var(--accent-2)]";
  const errorText = "mt-2 text-[12px] text-[#8a2f2f]";
  const t = language === "zh" ? {
    title: "用户资料",
    subtitle: "管理账号信息与联系方式",
    userId: "用户 ID",
    username: "用户名",
    email: "邮箱",
    save: "保存更改",
    loading: "加载中...",
    saving: "保存中...",
    updated: "资料已更新。",
    loadFail: "无法加载资料。",
    updateFail: "更新失败。",
  } : {
    title: "Profile",
    subtitle: "Manage your account details",
    userId: "User ID",
    username: "Username",
    email: "Email",
    save: "保存更改",
    loading: "Loading profile...",
    saving: "Saving changes...",
    updated: "Profile updated.",
    loadFail: "Unable to load profile.",
    updateFail: "Update failed.",
  };
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const loadProfile = async () => {
      setError("");
      try {
        setStatus(t.loading);
        const response = (await getMe()) as ApiEnvelope<UserProfile>;
        setProfile(response.data);
        setUsername(response.data.username);
        setEmail(response.data.email);
      } catch (err) {
        setError(err instanceof Error ? err.message : t.loadFail);
      } finally {
        setStatus("");
      }
    };

    void loadProfile();
  }, []);

  const handleSave = async () => {
    setError("");
    try {
      setStatus(t.saving);
      const response = (await updateMe({ username, email })) as ApiEnvelope<UserProfile>;
      setProfile(response.data);
      setStatus(t.updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : t.updateFail);
      setStatus("");
    }
  };

  return (
    <section className="mt-8 grid place-items-center">
      <div className="w-full max-w-[520px] rounded-[14px] border border-[var(--border)] bg-[linear-gradient(180deg,var(--surface),var(--surface-2))] px-5 py-[18px] shadow-[0_12px_24px_-22px_var(--shadow)]">
        <div className="mb-2.5">
          <h2 className="m-0 mb-3 text-[16px]">{t.title}</h2>
          <p className="m-0 text-[12px] text-[var(--muted)]">{t.subtitle}</p>
        </div>
        <div className="mb-3 flex items-center justify-between gap-3 rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-2.5 py-2 text-[12px] text-[var(--muted)]">
          <span>{t.userId}</span>
          <span>{profile?.userId ?? "-"}</span>
        </div>
        <label className={fieldBase}>
          <span>{t.username}</span>
          <input className={inputBase} value={username} onChange={(event) => setUsername(event.target.value)} />
        </label>
        <label className={fieldBase}>
          <span>{t.email}</span>
          <input className={inputBase} type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <div className="flex justify-end">
          <button className={`${buttonBase} ${buttonPrimary}`} onClick={handleSave}>
            {t.save}
          </button>
        </div>
        {status ? <p className={statusText}>{status}</p> : null}
        {error ? <p className={errorText}>{error}</p> : null}
      </div>
    </section>
  );
}
