import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useUiLanguage } from "../utils/ui";
import { devAttrs, withDevName } from "../utils/devNames";

function WelcomePage() {
  const navigate = useNavigate();
  const language = useUiLanguage();
  const [token, setToken] = useState(() => window.localStorage.getItem("auth_token"));

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

  const t = language === "zh"
    ? {
        brand: "City Platform",
        title: "SVG布局到3D模型流程",
        subtitle: "生成布局、编辑SVG，并准备三维模型转换。",
        primaryAction: "进入工作台",
        secondaryAction: "查看流程",
        login: "登录",
        register: "注册",
        workflowTitle: "工作流",
        workflowSubtitle: "像视频分段一样清晰的三步节奏",
        featuresTitle: "核心能力",
        featuresSubtitle: "从布局到模型，全流程集中管理",
        latestTitle: "最新动态",
        latestSubtitle: "设计记录与产品更新",
        blogTitle: "简介与更新",
        blogSubtitle: "了解平台定位与近期进展",
        readMore: "继续阅读",
        aboutTitle: "关于平台",
        aboutBody: "City Platform 专注于SVG布局到3D模型的完整流程。你可以从参数化布局开始，在线编辑图层，再生成三维模型模型进行审阅。",
        enterLayout: "进入布局编辑",
        enterModels: "进入模型预览",
        enterProfile: "进入个人中心",
      }
    : {
        brand: "City Platform",
        title: "SVG layout to 3D model pipeline",
        subtitle: "Generate a layout, tweak the SVG, and prepare it for 三维模型 conversion.",
        primaryAction: "进入工作台",
        secondaryAction: "查看流程",
        login: "登录",
        register: "注册",
        workflowTitle: "Workflow",
        workflowSubtitle: "Three clear stages, like a timeline",
        featuresTitle: "Core capabilities",
        featuresSubtitle: "One place to manage the layout-to-model flow",
        latestTitle: "Latest updates",
        latestSubtitle: "Design notes and product releases",
        blogTitle: "Intro & notes",
        blogSubtitle: "Positioning and recent progress",
        readMore: "继续阅读",
        aboutTitle: "About the platform",
        aboutBody: "City Platform focuses on the SVG-to-3D workflow. Start from parametric layouts, edit layers online, then generate 三维模型 models for review.",
        enterLayout: "进入布局编辑",
        enterModels: "进入模型预览",
        enterProfile: "进入个人中心",
      };

  const steps = language === "zh"
    ? [
        { title: "生成布局", note: "输入参数，生成SVG布局" },
        { title: "分层编辑", note: "开关图层，调整细节" },
        { title: "转换三维模型", note: "保存并输出3D模型" },
      ]
    : [
        { title: "Generate layout", note: "Submit params and get an SVG" },
        { title: "Layer editing", note: "Toggle layers and refine" },
        { title: "Convert to ", note: "Save and export 3D" },
      ];

  const posts = language === "zh"
    ? [
        { title: "布局生成已支持图层同步", date: "2026-02-10", note: "SVG层级与JSON一致，便于编辑。" },
        { title: "编辑器体验升级", date: "2026-02-08", note: "缩放、拖拽、删除操作更直观。" },
        { title: "三维模型预览流畅度优化", date: "2026-02-05", note: "Three.js加载与交互更顺滑。" },
      ]
    : [
        { title: "Layout generation syncs layers", date: "2026-02-10", note: "SVG layers stay aligned with JSON." },
        { title: "Editor experience refresh", date: "2026-02-08", note: "Zoom, drag, and delete feel smoother." },
        { title: "三维模型 preview tuning", date: "2026-02-05", note: "Three.js loading and controls improved." },
      ];

  const features = language === "zh"
    ? [
        { id: "layout", title: "布局编辑器", desc: "生成、预览并编辑SVG布局", path: "/layout", action: t.enterLayout },
        { id: "models", title: "3D模型预览", desc: "一键生成并旋转查看3D模型", path: "/models", action: t.enterModels },
        { id: "profile", title: "个人中心", desc: "账号与资源统一管理", path: "/profile", action: t.enterProfile },
      ]
    : [
        { id: "layout", title: "Layout editor", desc: "Generate, preview, and edit SVG layouts", path: "/layout", action: t.enterLayout },
        { id: "models", title: "3D model viewer", desc: "Generate and inspect 3D output", path: "/models", action: t.enterModels },
        { id: "profile", title: "Profile", desc: "Manage your account and assets", path: "/profile", action: t.enterProfile },
      ];

  const handleNavigate = (path: string, requiresAuth: boolean) => {
    if (requiresAuth && !token) {
      navigate("/auth/login", { state: { from: path } });
      return;
    }
    navigate(path);
  };

  const buttonBase =
    "inline-flex items-center justify-center rounded-full px-4 py-2 text-[13px] font-semibold transition-all duration-150 hover:-translate-y-0.5 hover:shadow-[0_10px_18px_-14px_var(--shadow)]";
  const buttonPrimary = "bg-[var(--accent)] text-white";
  const buttonGhost = "border border-[var(--border)] bg-transparent text-[var(--ink)]";

  return (
    <div {...devAttrs('WelcomePage')} className="mx-auto w-full grid min-h-screen  max-w-[1400px] gap-7 text-[var(--ink)] overflow-auto ">
      <section className="relative mx-1 mb-1 grid grid-cols-[minmax(0,1.35fr)_minmax(0,0.65fr)] gap-5 rounded-[22px] border border-[var(--border)] p-6 bg-[radial-gradient(circle_at_top_left,rgba(116,176,168,0.22),transparent_55%),linear-gradient(135deg,rgba(244,244,244,0.9),rgba(231,236,238,0.95))] dark:bg-[radial-gradient(circle_at_top_left,rgba(116,176,168,0.2),transparent_55%),linear-gradient(135deg,rgba(22,22,22,0.95),rgba(34,34,34,0.98))] after:pointer-events-none after:absolute after:inset-0 after:bg-[linear-gradient(120deg,transparent_0%,rgba(255,255,255,0.12)_50%,transparent_100%)] after:content-['']">
        <div className="relative z-[1]">
          <p className="mb-3 text-[12px] uppercase tracking-[0.32em] text-[var(--accent-2)]">{t.brand}</p>
          <h1 className="mb-3 text-[clamp(26px,3.4vw,40px)] tracking-[0.02em]">{t.title}</h1>
          <p className="mb-5 max-w-[520px] text-[16px] text-[var(--muted)]">{t.subtitle}</p>
          <div className="flex flex-wrap items-center gap-2.5">
            {token ? (
              <button
                className={`${buttonBase} ${buttonPrimary}`}
                type="button"
                onClick={() => navigate("/layout")}
              >
                {t.primaryAction}
              </button>
            ) : (
              <>
                <button
                  {...devAttrs('Welcome:LoginButton')}
                  className={`${buttonBase} ${buttonPrimary}`}
                  type="button"
                  onClick={() => navigate("/auth/login")}
                >
                  {t.login}
                </button>
                <button
                  {...devAttrs('Welcome:RegisterButton')}
                  className={`${buttonBase} ${buttonGhost}`}
                  type="button"
                  onClick={() => navigate("/auth/register")}
                >
                  {t.register}
                </button>
              </>
            )}
            <a className="text-[13px] text-[var(--accent)] hover:underline" href="#workflow">
              {t.secondaryAction}
            </a>
          </div>
        </div>
        <div className="relative z-[1] grid gap-3 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.55)] p-3.5 dark:bg-[rgba(20,20,20,0.65)]">
          <div className="text-[13px] uppercase tracking-[0.2em] text-[var(--muted)]">{t.latestTitle}</div>
          <div className="text-[13px] text-[var(--muted)]">{t.latestSubtitle}</div>
          <div className="grid gap-2.5">
            {posts.map((item) => (
              <div key={item.title} className="grid gap-1 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-2.5">
                <div className="text-[13px] font-semibold">{item.title}</div>
                <div className="text-[11px] uppercase tracking-[0.12em] text-[var(--accent-2)]">{item.date}</div>
                <div className="text-[12px] text-[var(--muted)]">{item.note}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-3.5 px-1 py-2.5" id="workflow">
        <div className="grid gap-1">
          <h2 className="text-[20px]">{t.workflowTitle}</h2>
          <p className="text-[13px] text-[var(--muted)]">{t.workflowSubtitle}</p>
        </div>
        <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-3">
          {steps.map((step, index) => (
            <div key={step.title} className="rounded-[14px] border border-[var(--border)] bg-[var(--surface)] p-3.5">
              <div className="text-[13px] font-bold text-[var(--accent-2)]">0{index + 1}</div>
              <div className="mt-1.5 text-[15px] font-semibold">{step.title}</div>
              <div className="mt-1 text-[13px] text-[var(--muted)]">{step.note}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-3.5 px-1 py-2.5">
        <div className="grid gap-1">
          <h2 className="text-[20px]">{t.featuresTitle}</h2>
          <p className="text-[13px] text-[var(--muted)]">{t.featuresSubtitle}</p>
        </div>
        <div className="grid grid-cols-[repeat(auto-fit,minmax(240px,1fr))] gap-3">
          {features.map((feature) => (
            <div key={feature.id} className="grid gap-2.5 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4">
              <div className="flex items-center justify-between gap-2.5">
                <h3 className="text-[16px]">{feature.title}</h3>
                <span className="text-[11px] uppercase tracking-[0.15em] text-[var(--accent-2)]">{token ? "Ready" : "Login"}</span>
              </div>
              <p className="text-[13px] text-[var(--muted)]">{feature.desc}</p>
              <button
                className={`${buttonBase} ${buttonPrimary}`}
                type="button"
                onClick={() => handleNavigate(feature.path, true)}
              >
                {feature.action}
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-3.5 px-1 py-2.5">
        <div className="grid gap-1">
          <h2 className="text-[20px]">{t.blogTitle}</h2>
          <p className="text-[13px] text-[var(--muted)]">{t.blogSubtitle}</p>
        </div>
        <div className="grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-3">
          {posts.map((post) => (
            <article key={post.title} className="grid gap-2 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4">
              <div className="text-[11px] uppercase tracking-[0.15em] text-[var(--accent-2)]">{post.date}</div>
              <h3 className="text-[15px]">{post.title}</h3>
              <p className="text-[13px] text-[var(--muted)]">{post.note}</p>
              <button className="text-left text-[13px] text-[var(--accent)] hover:underline" type="button">
                {t.readMore}
              </button>
            </article>
          ))}
          <article className="grid gap-2 rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-4">
            <div className="text-[11px] uppercase tracking-[0.15em] text-[var(--accent-2)]">{t.aboutTitle}</div>
            <h3 className="text-[15px]">{t.brand}</h3>
            <p className="text-[13px] text-[var(--muted)]">{t.aboutBody}</p>
          </article>
        </div>
      </section>

      <footer className="flex flex-col justify-between gap-3 text-[12px] text-[var(--muted)] md:flex-row">
        <span>City Platform © 2026</span>
        <span>SVG → 3D workflow</span>
      </footer>
    </div>
  );
}

export default withDevName(WelcomePage, 'WelcomePage');

