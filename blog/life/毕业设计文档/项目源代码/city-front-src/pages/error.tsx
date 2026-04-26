import { useNavigate, useRouteError } from "react-router-dom";
import { useUiLanguage } from "../utils/ui";

type RouteError = {
  status?: number;
  statusText?: string;
  message?: string;
};

export function ErrorPage() {
  const error = useRouteError() as RouteError;
  const navigate = useNavigate();
  const language = useUiLanguage();

  const t = language === "zh"
    ? {
        notFound: "页面未找到",
        serverError: "服务器错误",
        unauthorized: "未授权",
        forbidden: "禁止访问",
        fallback: "出错了",
        desc404: "抱歉，页面不存在或已被移除。",
        desc500: "服务器发生错误，请稍后再试。",
        desc401: "需要登录后才能访问此页面。",
        desc403: "你没有权限访问此页面。",
        descOther: "发生未知错误。",
        home: "返回首页",
        back: "返回上页",
      }
    : {
        notFound: "Page Not Found",
        serverError: "Server Error",
        unauthorized: "Unauthorized",
        forbidden: "Forbidden",
        fallback: "Oops! Something went wrong",
        desc404:
          "Sorry, the page you're looking for doesn't exist. It might have been moved or deleted.",
        desc500: "An unexpected error occurred on the server. Please try again later.",
        desc401: "You need to be logged in to access this page.",
        desc403: "You don't have permission to access this page.",
        descOther: "An unexpected error occurred.",
        home: "Go Home",
        back: "Go Back",
      };

  const status = error?.status || 404;
  const statusText = error?.statusText || "Not Found";
  const message = error?.message || "The page you're looking for doesn't exist.";
  const buttonBase = "inline-flex items-center justify-center rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-[12px] font-semibold transition-all duration-150 hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-16px_var(--shadow)]";
  const buttonPrimary = "border-transparent bg-[var(--accent)] text-white";
  const buttonGhost = "bg-transparent text-[var(--ink)]";

  const getErrorTitle = () => {
    switch (status) {
      case 404:
        return t.notFound;
      case 500:
        return t.serverError;
      case 401:
        return t.unauthorized;
      case 403:
        return t.forbidden;
      default:
        return t.fallback;
    }
  };

  const getErrorDescription = () => {
    switch (status) {
      case 404:
        return t.desc404;
      case 500:
        return t.desc500;
      case 401:
        return t.desc401;
      case 403:
        return t.desc403;
      default:
        return message || t.descOther;
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[linear-gradient(135deg,#667eea_0%,#764ba2_100%)] p-8">
      <div className="max-w-[600px] rounded-xl bg-white px-8 py-12 text-center shadow-[0_20px_60px_rgba(0,0,0,0.3)]">
        {/* status number: use viewport-clamped logical px to scale on different viewports */}
        <div className="m-0 text-[clamp(48px,10vw,96px)] font-bold text-[#667eea]">{status}</div>
        {/* main title: use fluid h1 token defined in styles.css */}
        <h1 className="my-4 text-[var(--fluid-h1)] font-semibold text-[#1a1a1a]">{getErrorTitle()}</h1>
        {/* paragraph text: prefer logical px tokens */}
        <p className="my-4 text-[var(--text-lg)] leading-relaxed text-[#666]">{getErrorDescription()}</p>

        {status === 401 && (
          <p className="my-6 break-all text-[var(--text-sm)] text-[#999]">
            <code className="rounded bg-[#f5f5f5] px-2 py-1 font-mono text-[#d32f2f]">{statusText}</code>
          </p>
        )}

        {status !== 401 && (
          <p className="my-6 break-all text-[var(--text-sm)] text-[#999]">
            {statusText}
            {message && ` - ${message}`}
          </p>
        )}

        <div className="mt-8 flex justify-center gap-4">
          <button className={`${buttonBase} ${buttonPrimary}`} onClick={() => navigate("/")}
          >
            {t.home}
          </button>
          <button className={`${buttonBase} ${buttonGhost}`} onClick={() => navigate(-1)}>
            {t.back}
          </button>
        </div>
      </div>
    </div>
  );
}
