import { Outlet, NavLink, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

export function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [token, setToken] = useState(() => window.localStorage.getItem("auth_token"));
  const language: "zh" = "zh";
  const [theme, setTheme] = useState<"light" | "dark">(
    (window.localStorage.getItem("uiTheme") as "light" | "dark") ?? "light"
  );
  const isWideShell = location.pathname === "/"
    || location.pathname.startsWith("/layout")
    || location.pathname.startsWith("/models");
  const isWorkspacePage = location.pathname.startsWith("/layout") || location.pathname.startsWith("/models");
  const isHome = location.pathname === "/" || location.pathname === "/welcome";
  const isAuth = location.pathname.startsWith("/auth");
  const isProfile = location.pathname.startsWith("/profile");

  const t = language === "zh"
    ? {
        brand: "City Platform",
        heroTitle: "SVG布局到3D模型流程",
        heroSubtitle: "生成布局、编辑SVG，并准备OBJ转换。",
        layout: "布局编辑",
        models: "模型预览",
        profile: "用户",
        login: "登录",
        register: "注册",
        logout: "退出",
        themeLight: "白昼",
        themeDark: "夜晚",
        langLabel: "语言",
      }
    : {
      brand: "City Platform",
        heroTitle: "SVG layout to 3D model pipeline",
        heroSubtitle: "Generate a layout, tweak the SVG, and prepare it for OBJ conversion.",
        layout: "布局编辑",
        models: "模型预览",
        profile: "用户",
        login: "登录",
        register: "注册",
        logout: "退出",
        themeLight: "白昼",
        themeDark: "夜晚",
        langLabel: "语言",
      };

  useEffect(() => {
    const refreshToken = () => {
      setToken(window.localStorage.getItem("auth_token"));
    };

    window.addEventListener("storage", refreshToken);
    window.addEventListener("auth:changed", refreshToken);
    return () => {
      window.removeEventListener("storage", refreshToken);
      window.removeEventListener("auth:changed", refreshToken);
    };
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.lang = "zh-CN";
    window.localStorage.setItem("uiTheme", theme);
    window.localStorage.setItem("uiLanguage", "zh");
    window.dispatchEvent(new Event("ui:changed"));
  }, [theme]);

  useEffect(() => {
    const refreshUi = () => {
      const storedTheme = (window.localStorage.getItem("uiTheme") as "light" | "dark") ?? "light";
      setTheme(storedTheme);
    };

    window.addEventListener("storage", refreshUi);
    window.addEventListener("ui:changed", refreshUi);
    return () => {
      window.removeEventListener("storage", refreshUi);
      window.removeEventListener("ui:changed", refreshUi);
    };
  }, []);

  const handleLogout = () => {
    window.localStorage.removeItem("auth_token");
    window.dispatchEvent(new Event("auth:changed"));
    setToken(null);
    navigate("/auth/login");
  };

  const topbarBase = "flex items-center mb-3 justify-between gap-3 rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-3 py-2 shadow-[0_8px_20px_-16px_var(--shadow)]";
  const topbarLayout = isHome ? "mx-auto w-full max-w-[1400px] px-1" : "w-full";
  const navLinkBase = "inline-flex items-center rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-[12px] font-semibold transition-all duration-150 hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-16px_var(--shadow)]";
  const buttonBase = "inline-flex items-center justify-center rounded-[10px] border border-[var(--border)] bg-transparent px-3 py-1.5 text-[12px] font-semibold transition-all duration-150 hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-16px_var(--shadow)]";
  const buttonSmall = "px-2.5 py-1 text-[11px]";
  const shellBase = `mx-auto w-full px-4 pt-2 animate-[rise_500ms_ease-out] flex flex-col ${isWorkspacePage ? "h-dvh pb-2" : "min-h-dvh pb-4"}`;
  const shellWidth = isHome ? "max-w-[1400px]" : isWideShell ? "max-w-[min(1800px,96vw)]" : "max-w-[1200px]";

  return (
    <div className={`${shellBase} ${shellWidth}`}>
      <header className={`${topbarBase} ${topbarLayout}`}>
        <div className={`flex items-center gap-2 ${isHome || isAuth || isProfile ? "min-h-[28px]" : ""}`}>
          {!isHome && !isAuth && !isProfile && token ? (
            <>
              <NavLink className={navLinkBase} to="/layout">
                {t.layout}
              </NavLink>
              <NavLink className={navLinkBase} to="/models">
                {t.models}
              </NavLink>
            </>
          ) : null}
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <div className="mr-2 flex items-center gap-2">
            <button
              className={`${buttonBase} ${buttonSmall}`}
              type="button"
              onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            >
              {theme === "light" ? t.themeLight : t.themeDark}
            </button>
          </div>
          {token ? (
            <>
              <NavLink className={navLinkBase} to="/profile">
                {t.profile}
              </NavLink>
              <button className={buttonBase} type="button" onClick={handleLogout}>
                {t.logout}
              </button>
            </>
          ) : null}
        </div>
      </header>
      <main className="flex-1 min-h-0">
        <Outlet />
      </main>
    </div>
  );
}
