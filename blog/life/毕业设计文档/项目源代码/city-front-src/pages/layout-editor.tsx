import { useEffect, useRef, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import {
  deleteLayout,
  generateLayout,
  getLayout,
  getLayoutJson,
  getLayoutProgress,
  listLayouts,
  saveLayout,
  saveLayoutArtifacts,
} from "@/api/layout";
import { generateModel, getModelProgress, getModelResult } from "@/api/model";
import { SvgPreview } from "@/components/svg/SvgPreview";
import { SvgTextEditor } from "@/components/svg/SvgTextEditor";
import { LayoutList } from "@/components/layout/LayoutList";
import { SvgEditorModal } from "@/components/modal/SvgEditorModal";
import { ArtifactsEditor } from "@/components/editor/ArtifactsEditor";
import { useLayoutEditorStore } from "@/pages/layout-editor/hooks/useLayoutEditorStore";
import {
  mapArtifactsToSaveRequest,
  mapLayoutJsonToArtifacts,
  normalizeGenerateLayoutId,
  normalizeLayoutJson,
  normalizeLayoutProgress,
  normalizeLayoutResult,
  normalizeLayouts,
  readLayoutId,
  readSvgContent,
  readSvgUrl,
} from "@/pages/layout-editor/service/layout-editor.service";
import { LayoutSelector } from "@/pages/layout-editor/view/LayoutSelector";
import type { ApiEnvelope } from "@/models/api-contract";
import { templateParams } from "@/models/api_templates";
import { LayoutGenerateRequest } from "@/models/layout-generate-request";
import type {
  LayoutArtifactsResponse,
  LayoutIdResponse,
  LayoutProgressResponse,
  SaveLayoutArtifactsResponse,
  LayoutSaveResponse,
} from "@/models/layout-api";
import type {
  GenerateModelProgressResponse,
  GenerateModelResponse,
  ModelResultResponse,
} from "@/models/model-api";
import type { LayoutResultResponse, LayoutsListItem } from "@/models/layout-result";
import { closeEditor } from "@/store/layout-editor-slice";
import { useAppDispatch } from "@/store/hooks";

function validateLayoutParams(obj: any): obj is LayoutGenerateRequest["params"] {
  // 简单校验主要字段
  if (!obj) return false;
  const keys = [
    "world_dimensions", "origin", "zoom", "tensor_field", "map", "style", "options", "download", "park_polygons"
  ];
  return keys.every((k) => k in obj);
}

function completeLayoutParams(obj: any): LayoutGenerateRequest["params"] {
  // 用模板补全缺失字段
  const result = { ...templateParams };
  if (obj) {
    if (typeof obj.world_dimensions !== "undefined") result.world_dimensions = obj.world_dimensions;
    if (typeof obj.origin !== "undefined") result.origin = obj.origin;
    if (typeof obj.zoom !== "undefined") result.zoom = obj.zoom;
    if (typeof obj.tensor_field !== "undefined") result.tensor_field = obj.tensor_field;
    if (typeof obj.map !== "undefined") result.map = obj.map;
    if (typeof obj.style !== "undefined") result.style = obj.style;
    if (typeof obj.options !== "undefined") result.options = obj.options;
    if (typeof obj.download !== "undefined") result.download = obj.download;
    if (typeof obj.park_polygons !== "undefined") result.park_polygons = obj.park_polygons;
  }
  return result;
}

// 布局编辑器页面主组件
// 负责布局参数管理、布局生成、SVG 编辑、要素编辑、历史记录、主题切换等核心功能



type LayoutTab = "preview" | "editor" | "library" | "artifacts";



export function LayoutEditorPage() {
  const dispatch = useAppDispatch();
  const {
    layoutId: layout_id,
    svgContent: svg_content,
    svgUrl,
    editingLayoutId: editinglayout_id,
    setLayoutId: setlayout_id,
    setSvgContent: setsvg_content,
    setSvgUrl,
    setEditingLayoutId: setEditinglayout_id,
  } = useLayoutEditorStore();
  const [params, setParams] = useState<LayoutGenerateRequest["params"]>(templateParams);
  const [responseMode, setResponseMode] = useState<"url" | "inline">("inline");
  const [layouts, setLayouts] = useState<LayoutsListItem[]>([]);
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [progress, setProgress] = useState<number>(0);
  const [phase, setPhase] = useState<string>("");
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [logLines, setLogLines] = useState<string[]>([]);
  const [authToken] = useState<string>(window.localStorage.getItem("auth_token") ?? "");
  const [tokenStatus, setTokenStatus] = useState("");
  const tokenTimerRef = useRef<number | null>(null);
  const [activeTab, setActiveTab] = useState<LayoutTab>("preview");
  const [artifactsLayoutId, setArtifactsLayoutId] = useState<string | null>(null);
  const [artifactsData, setArtifactsData] = useState<Record<string, any> | null>(null);
  const [artifactsStatus, setArtifactsStatus] = useState<string>("");
  const language: "zh" = "zh";
  const location = useLocation();
  const { tab } = useParams<{ tab?: string }>();
  const [theme, setTheme] = useState<"light" | "dark">(
    (window.localStorage.getItem("uiTheme") as "light" | "dark") ?? "light"
  );

  // ===================== SVG 编辑器相关 =====================
  const progressTimers = useRef<number[]>([]);

  const resolveTabParam = (value: string | null | undefined): LayoutTab | null => {
    if (value === "preview" || value === "editor" || value === "library" || value === "artifacts") {
      return value;
    }
    return null;
  };

  useEffect(() => {
    const searchTab = resolveTabParam(new URLSearchParams(location.search).get("tab"));
    const pathTab = resolveTabParam(tab ?? (location.pathname.endsWith("/artifacts") ? "artifacts" : null));
    const nextTab = searchTab ?? pathTab;
    if (nextTab && nextTab !== activeTab) {
      setActiveTab(nextTab);
    }
  }, [location.pathname, location.search, tab, activeTab]);

  useEffect(() => {
    if (!artifactsStatus) return;
    const shouldAutoHide =
      artifactsStatus.includes("已加载") ||
      artifactsStatus.includes("已提交保存") ||
      artifactsStatus.includes("已保存");
    if (!shouldAutoHide) return;
    const timer = window.setTimeout(() => {
      setArtifactsStatus((current) => {
        if (current.includes("已加载") || current.includes("已提交保存") || current.includes("已保存")) {
          return "";
        }
        return current;
      });
    }, 2000);
    return () => window.clearTimeout(timer);
  }, [artifactsStatus]);

  const toNumber = (value: string, fallback: number) => {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  };

  const updateParam = (path: Array<string | number>, value: unknown) => {
    setParams((current) => {
      const next = structuredClone(current);
      let cursor: any = next;
      for (let index = 0; index < path.length - 1; index += 1) {
        cursor = cursor[path[index]];
      }
      cursor[path[path.length - 1]] = value;
      return next;
    });
  };

  const appendLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogLines((current) => [...current.slice(-199), `[${timestamp}] ${message}`]);
  };

  const clearProgressTimers = () => {
    // ===================== 3D模型生成 =====================
    progressTimers.current.forEach((timerId) => window.clearTimeout(timerId));
    progressTimers.current = [];
  };

  const scrollToSection = (sectionId: string) => {
    const target = document.getElementById(sectionId);
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  const startProgress = () => {
    clearProgressTimers();
    setProgress(0);
    setPhase("初始化中...");

    // 简化进度条 - 只显示缓慢的增长，让用户知道在进行中
    const maxSteps = 10;
    const stepDuration = 500; // 每 500ms 增加一点进度

    for (let i = 1; i <= maxSteps; i++) {
      const timerId = window.setTimeout(() => {
        // ===================== 要素（Artifacts）加载与保存 =====================
        const nextProgress = Math.min(10 + i * 8, 90); // 10-90% 之间增长
        setProgress(nextProgress);
        setPhase(`处理中 (${nextProgress}%)...`);
      }, i * stepDuration);
      progressTimers.current.push(timerId);
    }
  };

  const refreshLayouts = async () => {
    try {
      const response = (await listLayouts()) as ApiEnvelope<LayoutsListItem[]> | LayoutsListItem[];
      setLayouts(normalizeLayouts(response));
    } catch {
      setLayouts([]);
    }
  };

  useEffect(() => {
    void refreshLayouts();
  }, []);



  // handleGenerate：发送符合新请求格式，并兼容多种返回字段
  const handleGenerate = async () => {
    setError("");
    if (!authToken) {
      setError("请先登录后再生成布局。");
      return;
    }

    setIsGenerating(true);
    setStatus("布局生成中...");
    appendLog("开始生成布局");

    const requestStartTime = Date.now();

    try {
      console.log(`%c[GENERATE] Sending request to /layout/generate`, 'color: #ff6600; font-weight: bold');

      const payload: LayoutGenerateRequest = {
        params,
        response_mode: responseMode,
        force_regenerate: true,
      };
      console.log('[参数管理] 最终请求体：', payload);

      const envelope = (await generateLayout(payload)) as ApiEnvelope<LayoutIdResponse> | LayoutIdResponse;

      console.log(`%c[GENERATE] generateLayout response:`, 'color: #0066cc; font-weight: bold', envelope);

      // 兼容多种后端返回格式：envelope.data.layout_id | envelope.data.layout_id | 直接返回 layout_id/layout_id
      const layout_idStr = normalizeGenerateLayoutId(envelope);

      if (!layout_idStr) {
        console.error('%c[GENERATE] ERROR: generateLayout did not return layout_id', 'color: #cc0000; font-weight: bold', envelope);
        throw new Error('服务未返回 layout_id');
      }

      // const layout_idStr = String(layout_idRaw);
      appendLog(`生成请求已提交：layout_id=${layout_idStr}`);

      // 轮询 /layout/progress/:layout_id，直到状态为 completed 或 failed
      let pollAttempts = 0;
      const maxPollAttempts = 600; // 3 分钟（600 * 300ms）
      let finalLayoutData: any = null;

      while (pollAttempts < maxPollAttempts) {
        pollAttempts++;
        try {
          const progressData = (await getLayoutProgress(layout_idStr)) as ApiEnvelope<LayoutProgressResponse> | LayoutProgressResponse;

          console.log(`%c[PROGRESS] poll #${pollAttempts}`, 'color: #0066cc', progressData);

          // int状态码映射到阶段和中文描述
          const stageInfo: Record<number, { key: string; progress: number; label: string }> = {
            10: { key: "stage_0", progress: 10, label: "基础布局生成" },
            20: { key: "stage_1", progress: 20, label: "水线生成" },
            30: { key: "stage_2", progress: 30, label: "水域多边形生成" },
            40: { key: "stage_3", progress: 40, label: "主干道生成" },
            50: { key: "stage_4", progress: 50, label: "大型公园生成" },
            60: { key: "stage_5", progress: 60, label: "次级道路生成" },
            70: { key: "stage_6", progress: 70, label: "小型公园生成" },
            80: { key: "stage_7", progress: 80, label: "多边形布局生成" },
            90: { key: "stage_8", progress: 90, label: "导出SVG与JSON" },
            100: { key: "done", progress: 100, label: "完成" },
            [-1]: { key: "failed", progress: -1, label: "失败" },
          };

          const progressPayload = normalizeLayoutProgress(progressData);
          const statusInt =
            typeof progressPayload?.status === "number"
              ? progressPayload.status
              : Number(progressPayload?.status);
          const info = stageInfo[statusInt];

          if (info) {
            setProgress(info.progress);
            setPhase(info.key === "failed" ? "生成失败" : info.label);
            setPhase(info.label);
          }

          // if (progressData?.phase) 
          // console.log(`%c[PROGRESS] status=${statusInt} (${info?.label ?? '未知阶段'}) progress=${progressPct}%`, 'color: #009933');
          if (statusInt === 100 || info?.key === 'done') {
            finalLayoutData = (await getLayout(layout_idStr)) as ApiEnvelope<LayoutResultResponse> | LayoutResultResponse;
            break;
          }
          if (statusInt === -1 || info?.key === 'failed') {
            setStatus("生成失败");
            setIsGenerating(false);
            throw new Error(progressPayload?.error || '生成失败');
          }
        } catch (pollErr) {
          console.warn('%c[PROGRESS] poll error', 'color: #ff9900', pollErr);
        }

        // 等待 300ms 再次轮询
        // eslint-disable-next-line no-await-in-loop
        await new Promise((r) => setTimeout(r, 300));
      }

      if (!finalLayoutData) {
        throw new Error('生成超时或未能获取最终布局数据');
      }
      else{
        console.log(`%c[GENERATE] Final layout data:`, 'color: #009933; font-weight: bold', finalLayoutData);
      }

      const layout = normalizeLayoutResult(finalLayoutData);
      
      // 兼容最终数据中的字段名
      const finallayout_id = readLayoutId(layout);
      if (finallayout_id) setlayout_id(String(finallayout_id));

      const normalizedSvgContent = readSvgContent(layout);
      if (normalizedSvgContent) {
        console.log('[GENERATE] svg_content:', normalizedSvgContent);
        setsvg_content(normalizedSvgContent);
      }
      setSvgUrl(readSvgUrl(layout));

      setProgress(100); 
      setPhase('已完成');
      setStatus('已就绪');
      appendLog(`布局已生成：layout_id=${layout_idStr}`);
      await refreshLayouts();
      // 生成完成后自动切换到预览界面并滚动到SVG预览
      setActiveTab("preview");
      setTimeout(() => {
        scrollToSection("svg-preview");
      }, 100);
    } catch (err) {
      clearProgressTimers();
      setPhase("失败");
      setStatus("失败");

      const errorMsg = err instanceof Error ? err.message : "布局生成失败。";
      setError(errorMsg);
      appendLog(`错误：${errorMsg}`);

      console.error(
        `%c[GENERATE] ERROR`,
        'color: #cc0000; font-weight: bold; font-size: 13px',
        errorMsg
      );
    } finally {
      setIsGenerating(false);
    }
  };

  // 新增：打开可视化编辑器
  const handleEditLayout = async (lid: string) => {
    try {
      console.log(`[EDIT] Loading layout for editing: ${lid}`);
      setActiveTab("artifacts");
      setArtifactsLayoutId(lid);

      const response = (await getLayout(lid)) as ApiEnvelope<LayoutResultResponse> | LayoutResultResponse;
      const layout = normalizeLayoutResult(response);
      if (layout) {
        setEditinglayout_id(lid);

        if (layout.params) {
          localStorage.setItem(`layout_params_${lid}`, JSON.stringify(layout.params));
        }

        setlayout_id(readLayoutId(layout));
        // 检查svg_content字段并输出内容
        const svgContent = readSvgContent(layout);
        if (svgContent) {
          console.log(`[EDIT] svg_content for layout #${lid}:`, svgContent);
        } else {
          console.warn(`[EDIT] svg_content for layout #${lid} is empty or missing.`);
        }
        setsvg_content(svgContent);
        setSvgUrl(readSvgUrl(layout));
        await handleLoadArtifacts(lid);
        scrollToSection("layout-artifacts");
        appendLog(`Opening artifacts editor for layout #${lid}`);
      }
    } catch (error) {
      console.error("Failed to load layout for editing:", error);
      setError("无法加载布局内容");
      appendLog(`加载布局出错：${error}`);
    }
  };
  // ===================== 令牌复制提示 =====================

  // 新增：保存编辑后的SVG
  const handleSaveEditedSvg = async (svg_content: string) => {
    if (!editinglayout_id) return;

    try {
      console.log(`[EDIT] Saving edited SVG for layout #${editinglayout_id}`);
      await saveLayout({
        layoutId: Number(editinglayout_id),
        svgContent: svg_content,
        responseMode: "inline",
      });

      appendLog(`Layout #${editinglayout_id} saved successfully`);
      dispatch(closeEditor());

      // 刷新布局列表
      const responseList = (await listLayouts()) as ApiEnvelope<LayoutsListItem[]> | LayoutsListItem[];
      setLayouts(normalizeLayouts(responseList));

      // 如果当前显示的是这个布局，更新SVG内容
      if (layout_id === editinglayout_id) {
        setsvg_content(svg_content);
      }
    } catch (error) {
      // ===================== 道路类型标签 =====================
      console.error("Failed to save edited SVG:", error);
      setError("保存失败");
      appendLog(`Error saving SVG: ${error}`);
    }
  };

  // 新增：生成3D模型
  const handleGenerateModel = async (lid: string) => {
    try {
      appendLog(`开始生成 3D 模型：布局 #${lid}...`);

      const kickoff = (await generateModel({
        layout_id: lid,
        response_mode: "url",
      })) as ApiEnvelope<GenerateModelResponse> | GenerateModelResponse;

      const kickoffData =
        kickoff && typeof kickoff === "object" && "data" in kickoff
          ? ((kickoff as ApiEnvelope<GenerateModelResponse>).data ?? {})
          : (kickoff as GenerateModelResponse);

      if (typeof kickoffData?.status === "number" && kickoffData.status < 0) {
        throw new Error(kickoffData.message || "模型生成启动失败");
      }

      appendLog(kickoffData?.message || `模型生成任务已提交：layout_id=${lid}`);

      const statusLabel: Record<number, string> = {
        10: "启动",
        80: "生成中",
        100: "生成结束",
      };

      let done = false;
      for (let attempt = 0; attempt < 120; attempt += 1) {
        const progressResponse = (await getModelProgress(lid)) as ApiEnvelope<GenerateModelProgressResponse> | GenerateModelProgressResponse;
        const progressData =
          progressResponse && typeof progressResponse === "object" && "data" in progressResponse
            ? ((progressResponse as ApiEnvelope<GenerateModelProgressResponse>).data ?? {})
            : (progressResponse as GenerateModelProgressResponse);

        const progressStatus = Number(progressData?.status);
        if (Number.isFinite(progressStatus)) {
          appendLog(`模型进度：${statusLabel[progressStatus] ?? progressStatus}`);
        }

        if (progressStatus === 100) {
          done = true;
          break;
        }

        if (progressStatus < 0) {
          throw new Error(progressData?.message || "模型生成失败");
        }

        // eslint-disable-next-line no-await-in-loop
        await new Promise((resolve) => setTimeout(resolve, 800));
      }

      if (!done) {
        throw new Error("模型生成超时，请稍后重试。");
      }

      const resultResponse = (await getModelResult(lid)) as ApiEnvelope<ModelResultResponse> | ModelResultResponse;
      const resultData =
        resultResponse && typeof resultResponse === "object" && "data" in resultResponse
          ? ((resultResponse as ApiEnvelope<ModelResultResponse>).data ?? {})
          : (resultResponse as ModelResultResponse);
      const firstModel = Array.isArray(resultData?.models) ? resultData.models[0] : undefined;

      if (!firstModel) {
        appendLog(`模型生成完成，但暂未返回可用模型文件：layout_id=${lid}`);
        return;
      }

      appendLog(`模型生成完成：modelId=${firstModel.modelId ?? "-"}`);
    } catch (error) {
      console.error("Failed to generate model:", error);
      setError("模型生成失败");
      appendLog(`Error generating model: ${error}`);
    }
  };

  useEffect(() => {
    if (activeTab !== "artifacts") {
      return;
    }
    void handleLoadArtifacts();
  }, [activeTab]);

  const handleLoadArtifacts = async (targetlayout_id?: string) => {
    const selectedId = targetlayout_id ?? artifactsLayoutId ?? layout_id;
    if (!selectedId) {
      setArtifactsStatus("");
      return;
    }
    try {
      setArtifactsStatus("要素加载中...");
      setArtifactsLayoutId(selectedId);
      const response = (await getLayoutJson(selectedId)) as ApiEnvelope<LayoutArtifactsResponse> | LayoutArtifactsResponse;
      const layoutJson = normalizeLayoutJson(response);
      const artifacts = mapLayoutJsonToArtifacts(layoutJson);
      setArtifactsData((artifacts as Record<string, any>) ?? {});
      setArtifactsStatus("要素已加载。");
    } catch (error) {
      console.error("Failed to load artifacts:", error);
      setArtifactsStatus("要素加载失败。");
    }
  };

  const handleSaveArtifacts = async () => {
    const selectedId = artifactsLayoutId ?? layout_id;
    if (!selectedId) {
      setArtifactsStatus("");
      return;
    }
    try {
      setArtifactsStatus("要素保存中...");
      const payload = mapArtifactsToSaveRequest(artifactsData);
      const response = (await saveLayoutArtifacts(selectedId, payload)) as ApiEnvelope<SaveLayoutArtifactsResponse>;
      const saved = Boolean(response?.data?.updated);
      setArtifactsStatus(saved ? "要素已保存。" : "要素已提交保存。");
    } catch (error) {
      console.error("Failed to save artifacts:", error);
      setArtifactsStatus("要素保存失败，请检查 JSON 格式。");
    }
  };

  const handleSelect = async (selectedId: string, targetTab: LayoutTab = "preview") => {
    setError("");
    try {
      const response = (await getLayout(selectedId)) as ApiEnvelope<LayoutResultResponse> | LayoutResultResponse;
      const layout = normalizeLayoutResult(response);
      if (!layout) {
        throw new Error("布局数据为空");
      }
      setlayout_id(readLayoutId(layout));
      setArtifactsLayoutId(readLayoutId(layout));
      setSvgUrl(readSvgUrl(layout));
      setsvg_content(readSvgContent(layout));
      if (layout.params) {
        const paramsRaw = layout.params as unknown;
        if (validateLayoutParams(paramsRaw)) {
          setParams(paramsRaw);
        } else {
          console.warn("[参数校验] 后端返回 params 字段缺失或类型不符，已自动补全。", paramsRaw);
          setParams(completeLayoutParams(paramsRaw));
        }
      }
      if (activeTab === "artifacts") {
        void handleLoadArtifacts(readLayoutId(layout) ?? undefined);
      }
      setActiveTab(targetTab);
      setTimeout(() => {
        if (targetTab === "preview") {
          const previewSection = document.getElementById("svg-preview-section");
          if (previewSection) {
            previewSection.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        }

        if (targetTab === "editor") {
          const editorSection = document.getElementById("layout-editor");
          if (editorSection) {
            editorSection.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        }
      }, 100);
    } catch (err) {
      setError(err instanceof Error ? err.message : "无法加载布局。");
    }
  };

  const handleLoadFromLibrary = async (selectedId: string) => {
    await handleSelect(selectedId, "preview");
  };

  const handleDelete = async (selectedId: string) => {
    setError("");
    try {
      console.log(`[DELETE] 请求路径: /api/layout/delete/${selectedId}`);
      await deleteLayout(selectedId);
      const responseList = (await listLayouts()) as ApiEnvelope<LayoutsListItem[]> | LayoutsListItem[];
      setLayouts(normalizeLayouts(responseList));
      if (layout_id === selectedId) {
        setlayout_id(null);
        setSvgUrl("");
        setsvg_content("");
      }
      if (artifactsLayoutId === selectedId) {
        setArtifactsLayoutId(null);
        setArtifactsData(null);
      }
      // ===================== 组件渲染结束 =====================
    } catch (err) {
      setError(err instanceof Error ? err.message : "删除失败。");
    }
  };

  const handleSave = async () => {
    setError("");
    if (!layout_id) {
      setError("请先生成布局。");
      return;
    }

    if (!svg_content && !svgUrl) {
      setError("没有可保存的 SVG 内容。");
      return;
    }

    try {
      setStatus("正在保存 SVG...");
      appendLog("正在保存 SVG 内容");
      const response = (await saveLayout({
        layoutId: Number(layout_id),
        svgContent: svg_content,
        responseMode,
      })) as ApiEnvelope<LayoutSaveResponse>;

      setsvg_content(response.data.svg_content ?? svg_content);
      setSvgUrl(response.data.svgUrl ?? svgUrl);
      setStatus("SVG 已保存。");
      appendLog("SVG 已保存");
      const responseList = (await listLayouts()) as ApiEnvelope<LayoutsListItem[]> | LayoutsListItem[];
      setLayouts(normalizeLayouts(responseList));
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存失败。");
      setStatus("");
      appendLog("保存失败");
    }
  };

  useEffect(() => {
    window.localStorage.setItem("uiTheme", theme);
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

  const labels = {
    zh: {
      artifactsHint: "点击添加点，拖拽调整。当前层:",
      title: "布局编辑器",
      mode: "模式",
      params: "参数",
      preview: "预览",
      editor: "文本",
      library: "历史",
      artifacts: "编辑",
      status: "状态",
      layoutParams: "布局参数",
      // auth_token: "认证令牌",
      // copyToken: "复制令牌",
      // tokenCopied: "已复制",
      // tokenMissing: "暂无令牌",
      tokenCopyFailed: "复制失败",
      svgPreview: "SVG 预览",
      svgEditor: "SVG 编辑",
      artifactsEditor: "要素编辑器",
      generationStatus: "生成状态",
      generateLayout: "生成布局",
      saveSvg: "保存 SVG",
      loadArtifacts: "加载要素",
      saveArtifacts: "保存要素",
      streamlines: "流线",
      polygons: "多边形",
      layout_id: "布局 ID",
      layoutSelect: "选择布局",
      listTitle: "布局历史",
      listFilter: "状态",
      listAll: "全部",
      listDraft: "草稿",
      listRunning: "生成中",
      listDone: "已完成",
      listGrid: "网格",
      listList: "列表",
      listCount: "数量",
      listEmpty: "暂无布局记录",
      listEmptyHint: "点击生成布局开始",
      listEdit: "编辑",
      listGenerate: "生成模型",
      listLoad: "预览",
      listRemove: "删除",
      listCreatedAt: "创建时间",
      listPrefix: "布局",
      gridLabel: "网格",
      zoomLabel: "缩放",
      deletePoint: "删除点",
      showLayers: "显示图层",
      hideLayers: "隐藏图层",
      // artifactsHint: "点击添加点，拖拽调整。当前层:",
      themeLight: "白昼",
      themeDark: "夜晚",
      languageLabel: "语言",

      responseUrl: "URL",
      svgSourceEmpty: "空",
      sourceLabel: "来源",
      worldSection: "世界",
      worldDimensions: "世界尺寸",
      origin: "原点",
      zoom: "缩放",
      tensorField: "张量场",
      smooth: "平滑",
      setRecommended: "设为推荐",
      grids: "网格",
      gridItem: "网格",
      addGrid: "添加网格",
      radials: "放射",
      radialItem: "放射",
      addRadial: "添加放射",
      mapSection: "地图",
      animate: "动画",
      animateSpeed: "动画速度",
      water: "水系",
      riverBankSize: "河岸宽度",
      riverSize: "河流宽度",
      coastlineNoise: "海岸噪声",
      riverNoise: "河道噪声",
      enabled: "启用",
      noiseSize: "噪声尺寸",
      noiseAngle: "噪声角度",
      simplifyTolerance: "简化容差",
      waterDevParams: "水系调参",
      devSep: "分离",
      devTest: "测试",
      devPath: "迭代",
      devSeed: "种子",
      devStep: "步长",
      devLookahead: "前瞻",
      devCircleJoin: "并合",
      devJoinAngle: "夹角",
      devSimplify: "简化",
      devCollide: "碰撞",
      roads: "道路",
      roadMain: "主干道",
      roadMajor: "主路",
      roadMinor: "支路",
      parks: "公园",
      clusterBigParks: "聚合大公园",
      parkBigCount: "大公园数",
      parkSmallCount: "小公园数",
      numBigParks: "大公园数量",
      numSmallParks: "小公园数量",
      buildings: "建筑",
      buildingMinArea: "最小面积",
      buildingMaxLength: "最大长度",
      buildingShrinkSpacing: "收缩间距",
      buildingNoDivide: "不拆分率",
      style: "风格",
      colourScheme: "配色方案",
      zoomBuildings: "放大建筑",
      buildingModels: "建筑模型",
      showFrame: "显示边框",
      orthographic: "正交视图",
      options: "选项",
      drawCenter: "绘制中心",
      highDpi: "高DPI",
      download: "下载",
      imageScale: "图像缩放",
      typeLabel: "类型",
      parkPolygons: "公园多边形",
      polygonMaxLength: "最大长度",
      polygonMinArea: "最小面积",
      polygonShrinkSpacing: "收缩间距",
      polygonNoDivide: "不拆分率",
      resetTemplate: "重置为模板",
      removeItem: "移除",
      coastlineWidth: "海岸线宽度"
    },
  };

  const t = labels.zh;
  // const responseModeLabel = responseMode === "inline" ? t.responseInline : t.responseUrl;

  const showTokenStatus = (message: string) => {
    setTokenStatus(message);
    if (tokenTimerRef.current) {
      window.clearTimeout(tokenTimerRef.current);
    }
    tokenTimerRef.current = window.setTimeout(() => setTokenStatus(""), 2000);
  };

  // const handleCopyToken = async () => {
  //   if (!authToken) {
  //     showTokenStatus(t.tokenMissing);
  //     return;
  //   }
  //   try {
  //     await navigator.clipboard.writeText(authToken);
  //     showTokenStatus(t.tokenCopied);
  //   } catch (error) {
  //     console.error("Failed to copy token:", error);
  //     showTokenStatus(t.tokenCopyFailed);
  //   }
  // };

  useEffect(() => () => {
    if (tokenTimerRef.current) {
      window.clearTimeout(tokenTimerRef.current);
    }
  }, []);
  const roadLabels = {
    main: "主干道",
    major: "主路",
    minor: "支路",
  };

  const layoutListLabels = {
    title: "",
    filterLabel: t.listFilter,
    filterAll: t.listAll,
    filterDraft: t.listDraft,
    filterRunning: t.listRunning,
    filterDone: t.listDone,
    viewGrid: t.listGrid,
    viewList: t.listList,
    count: t.listCount,
    emptyTitle: t.listEmpty,
    emptyHint: t.listEmptyHint,
    statusDraft: t.listDraft,
    statusRunning: t.listRunning,
    statusDone: t.listDone,
    edit: t.listEdit,
    generate: t.listGenerate,
    load: t.listLoad,
    remove: t.listRemove,
    createdAt: t.listCreatedAt,
    layoutPrefix: t.listPrefix,
    confirmDelete: (id: string) => `${t.listRemove} ${t.listPrefix} #${id}?`,
  };

  const artifactsLabels = {
    layer: t.artifacts,
    feature: t.streamlines,
    grid: t.gridLabel,
    zoom: t.zoomLabel,
    deletePoint: t.deletePoint,
    showLayers: t.showLayers,
    hideLayers: t.hideLayers,
    hint: t.artifactsHint,
  };

  const resolvePreviewUrl = (url: string) => {
    if (!url) return url;
    if (url.includes("tensor_visualization.svg")) {
      return url.replace("tensor_visualization.svg", "blocks.svg");
    }
    if (url.endsWith("layout.svg")) {
      return url.replace("layout.svg", "blocks.svg");
    }
    return url;
  };

  const buttonBase = "max-w-full rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-2.5 py-1.5 text-[12px] font-semibold transition-all duration-150 hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-16px_var(--shadow)] disabled:cursor-not-allowed disabled:opacity-60";
  const buttonPrimary = "border-transparent bg-[var(--accent)] text-yellow";
  const buttonGhost = "bg-transparent text-[var(--ink)]";
  const buttonSmall = "px-3";
  const panelBase = "min-w-0 w-full max-w-full rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-1.5 py-2.5 shadow-[0_12px_24px_-22px_var(--shadow)]";
  const panelHeaderBase = "flex items-baseline justify-between gap-3";
  const panelHeaderCompact = "flex items-center justify-between gap-3";
  const panelTitleBase = "m-0 mb-3 text-[16px]";
  const fieldBase = "flex min-w-0 w-full flex-wrap items-center gap-2 mb-3 text-[12px]";
  const fieldInline = "gap-2 mb-0";
  const inputBase = "min-w-0 max-w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2 py-1.5 text-[12px] text-[var(--ink)]";
  const buttonRowBase = "flex min-w-0 w-full flex-wrap gap-2 mt-3 [&>*]:min-w-0 [&>*]:max-w-full [&>input]:flex-1 [&>input]:basis-[calc(50%-0.25rem)] [&>select]:flex-1 [&>select]:basis-[calc(50%-0.25rem)]";
  const buttonRowCompact = "gap-1.5 mt-1.5";
  const sliderRowBase = "grid min-w-0 w-full grid-cols-[minmax(0,1fr)_80px] gap-3 items-center";
  const paramGridBase = "grid min-w-0 gap-1.5 md:grid-cols-[repeat(auto-fit,minmax(200px,1fr))]";
  const paramPairBase = "grid min-w-0 grid-cols-[minmax(56px,auto)_minmax(0,1fr)] items-center gap-1.5";
  const layoutSelectBase = "inline-flex items-center gap-1.5 text-[11px] text-[var(--muted)]";
  const workspaceShell = "grid h-full min-h-0 gap-3 overflow-hidden";
  const workspaceBody = "grid h-full min-h-0 grid-cols-1 gap-3 overflow-hidden";
  const workspaceMain = "h-full min-h-0 overflow-hidden";
  const workspaceColumns = "grid h-full min-h-0 min-w-0 gap-3 lg:grid-cols-[minmax(0,clamp(280px,24vw,340px))_minmax(0,1fr)]";
  const workspaceFrame = "h-full min-h-0 min-w-0 max-h-full w-full max-w-full rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-1.5 py-3";
  const workspacePane = "flex h-full min-h-0 min-w-0 max-h-full w-full max-w-full flex-col";
  const workspacePreviewPane = "flex h-full min-h-0 max-h-full min-w-0 flex-col gap-3 overflow-hidden";
  const paramsScroll = "pretty-scrollbar flex h-full min-h-0 max-h-full flex-1 flex-col gap-3 overflow-y-auto overflow-x-hidden overscroll-contain [scrollbar-gutter:stable_both-edges] px-0 text-[12px]";
  const collapsePanel = "grid shrink-0 grid-cols-1 min-w-0 w-full max-w-full rounded-[10px] border border-[var(--border)] bg-[var(--surface)] shadow-[0_10px_22px_-20px_var(--shadow)]";
  const collapseTitle = "list-none block min-w-0 w-full max-w-full overflow-hidden text-ellipsis whitespace-nowrap cursor-pointer border-b border-[var(--border)] bg-[var(--surface-2)] px-1.5 py-2 text-[13px] font-semibold [&::-webkit-details-marker]:hidden [&::marker]:hidden";
  const collapseBody = "grid min-w-0 w-full max-w-full gap-1.5 overflow-x-hidden px-1.5 pb-2.5 pt-2";
  const tabHeader = "flex flex-wrap gap-2 border-b border-[var(--border)] pb-2";
  const tabButtonBase = "rounded-lg border border-transparent px-3 py-1 text-[12px] font-semibold text-[var(--muted)] transition-colors hover:bg-[var(--surface-2)] hover:text-[var(--ink)]";
  const tabButtonActive = "border-[var(--border)] bg-[var(--surface-2)] text-[var(--ink)]";
  const tabPanelScroll = "pretty-scrollbar flex-1 h-0 min-h-0 max-h-full overflow-auto";
  const tabPanelClip = "flex-1 h-0 min-h-0 max-h-full overflow-hidden";
  const metaBase = "flex flex-wrap items-center gap-2 text-[12px] text-[var(--muted)]";
  const listBase = "grid gap-2";
  const listItemBase = "flex items-center justify-between gap-3 rounded-lg border border-[var(--border)] bg-[var(--surface-2)] px-3 py-2 text-[12px]";
  const statusText = "mt-2 text-[12px] text-[var(--accent-2)]";
  const errorText = "mt-2 text-[12px] text-[#8a2f2f]";
  const floatPanel = "pretty-scrollbar fixed right-4 top-4 z-40 w-[min(420px,calc(100vw-32px))] max-h-[calc(100vh-32px)] overflow-auto rounded-[10px] border border-[var(--border)] bg-[var(--surface)] p-4 text-[var(--ink)] shadow-[0_12px_24px_-20px_var(--shadow)]";
  const floatHeader = "flex items-center justify-between gap-3";
  const floatTitle = "m-0 mb-2 text-[12px] font-semibold uppercase tracking-[0.04em] text-[var(--muted)]";
  const progressBar = "h-2.5 w-full overflow-hidden rounded-full bg-[var(--surface-2)]";
  const progressFill = "h-full bg-[linear-gradient(90deg,var(--accent),var(--accent-2))] transition-[width] duration-300";
  const paramSection = "grid gap-2";
  const paramSectionHeader = "flex min-w-0 flex-wrap items-center justify-between gap-2";
  const paramCardList = "grid min-h-0 auto-rows-auto gap-2";
  const paramCard = "min-w-0 w-full max-w-full rounded-[10px] border border-[var(--border)] bg-[var(--surface)] shadow-[0_8px_18px_-16px_var(--shadow)]";
  const paramCardHeader = "border-b border-[var(--border)] bg-[var(--surface-2)] px-2.5 py-1 text-[12px] font-semibold";
  const paramCardBody = "grid min-w-0 w-full gap-2 p-2.5";
  const paramRowBase = "flex min-w-0 w-full flex-wrap gap-2 overflow-x-hidden";
  const paramItemBase = "flex min-w-0 max-w-full flex-1 basis-[calc(50%-0.25rem)] items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2 py-1";
  const paramLabelBase = "min-w-[36px] text-[11px] text-[var(--muted)] whitespace-nowrap";
  const paramInputBase = `${inputBase} w-16 px-1.5 py-1 text-[11px]`;

  const handleLayoutSelect = (value: string) => {
    if (!value) return;
    void handleSelect(value, activeTab === "editor" ? "editor" : "preview");
  };

  const handleArtifactsLayoutSelect = (value: string) => {
    if (!value) return;
    setArtifactsLayoutId(value);
    setlayout_id(value);
    void handleLoadArtifacts(value);
  };

  return (
    <section className={workspaceShell}>
      <div className={workspaceBody}>
        <div className={workspaceMain}>
          {/* 参数面板的外部边框 */}
          <div className={workspaceColumns}>
            <div className={workspaceFrame}>
              <div className={workspacePane}>
                <div className={paramsScroll}>
     <div
  className={`${panelBase} shrink-0 flex items-center justify-center text-center text-[15px] font-semibold tracking-wide text-[var(--ink)] bg-[var(--surface-2)] rounded-xl py-3`}
  id="layout-params"
>
  {t.layoutParams}
</div>



                <details className={collapsePanel} open>
                  <summary className={collapseTitle}>{t.worldSection}</summary>
                  <div className={collapseBody}>
                    <div className={fieldBase}>
                      <span>{t.worldDimensions}</span>
                      <div className={buttonRowBase}>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.world_dimensions.x}
                          onChange={(event) =>
                            updateParam(["world_dimensions", "x"], toNumber(event.target.value, params.world_dimensions.x))
                          }
                        />
                        <input
                          className={inputBase}
                          type="number"
                          value={params.world_dimensions.y}
                          onChange={(event) =>
                            updateParam(["world_dimensions", "y"], toNumber(event.target.value, params.world_dimensions.y))
                          }
                        />
                      </div>
                    </div>
                    <div className={fieldBase}>
                      <span>{t.origin}</span>
                      <div className={buttonRowBase}>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.origin.x}
                          onChange={(event) =>
                            updateParam(["origin", "x"], toNumber(event.target.value, params.origin.x))
                          }
                        />
                        <input
                          className={inputBase}
                          type="number"
                          value={params.origin.y}
                          onChange={(event) =>
                            updateParam(["origin", "y"], toNumber(event.target.value, params.origin.y))
                          }
                        />
                      </div>
                    </div>
                    <div className={fieldBase}>
                      <span>{t.zoom}</span>
                      <div className={sliderRowBase}>
                        <input
                          type="range"
                          min="0.01"
                          max="1"
                          step="0.01"
                          value={params.zoom}
                          onChange={(event) => updateParam(["zoom"], toNumber(event.target.value, params.zoom))}
                        />
                        <input
                          className={inputBase}
                          type="number"
                          step="0.01"
                          value={params.zoom}
                          onChange={(event) => updateParam(["zoom"], toNumber(event.target.value, params.zoom))}
                        />
                      </div>
                    </div>
                  </div>
                </details>

                <details className={collapsePanel}>
                  <summary className={collapseTitle}>{t.tensorField}</summary>
                  <div className={collapseBody}>
                    <label className={fieldBase}>
                      <span>{t.smooth}</span>
                      <input
                        type="checkbox"
                        checked={params.tensor_field.smooth}
                        onChange={(event) => updateParam(["tensor_field", "smooth"], event.target.checked)}
                      />
                    </label>
                    <label className={fieldBase}>
                      <span>{t.setRecommended}</span>
                      <input
                        type="checkbox"
                        checked={params.tensor_field.set_recommended}
                        onChange={(event) =>
                          updateParam(["tensor_field", "set_recommended"], event.target.checked)
                        }
                      />
                    </label>
                    <div className={paramSection}>
                      <div className={paramSectionHeader}>
                        <h4 className={panelTitleBase}>{t.grids}</h4>
                        <button
                          className={buttonBase}
                          type="button"
                          onClick={() =>
                            updateParam(["tensor_field", "grids"], [
                              ...params.tensor_field.grids,
                              { x: 0, y: 0, size: 48, decay: 10, theta: 0 },
                            ])
                          }
                        >
                          {t.addGrid}
                        </button>
                      </div>
                      <div className={paramCardList}>
                        {params.tensor_field.grids.map((grid: any, index: any) => (
                          <div key={`grid-${index}`} className={paramCard}>
                            <div className={paramCardHeader}>
                              <span>{t.gridItem} {index + 1}</span>
                            </div>
                            <div className={paramCardBody}>
                              <div className={paramRowBase}>
                                <label className={paramItemBase}>
                                  <span className={paramLabelBase}>X</span>
                                  <input
                                    className={paramInputBase}
                                    type="number"
                                    value={grid.x}
                                    onChange={(event) =>
                                      updateParam(["tensor_field", "grids", index, "x"], toNumber(event.target.value, grid.x))
                                    }
                                  />
                                </label>
                                <label className={paramItemBase}>
                                  <span className={paramLabelBase}>Y</span>
                                  <input
                                    className={paramInputBase}
                                    type="number"
                                    value={grid.y}
                                    onChange={(event) =>
                                      updateParam(["tensor_field", "grids", index, "y"], toNumber(event.target.value, grid.y))
                                    }
                                  />
                                </label>
                                <label className={paramItemBase}>
                                  <span className={paramLabelBase}>尺寸</span>
                                  <input
                                    className={paramInputBase}
                                    type="number"
                                    value={grid.size}
                                    onChange={(event) =>
                                      updateParam(["tensor_field", "grids", index, "size"], toNumber(event.target.value, grid.size))
                                    }
                                  />
                                </label>
                                <label className={paramItemBase}>
                                  <span className={paramLabelBase}>衰减</span>
                                  <input
                                    className={paramInputBase}
                                    type="number"
                                    value={grid.decay}
                                    onChange={(event) =>
                                      updateParam(["tensor_field", "grids", index, "decay"], toNumber(event.target.value, grid.decay))
                                    }
                                  />
                                </label>
                                <label className={paramItemBase}>
                                  <span className={paramLabelBase}>角度</span>
                                  <input
                                    className={paramInputBase}
                                    type="number"
                                    value={grid.theta}
                                    onChange={(event) =>
                                      updateParam(["tensor_field", "grids", index, "theta"], toNumber(event.target.value, grid.theta))
                                    }
                                  />
                                </label>
                              </div>
                              <button
                                className={`${buttonBase} ${buttonSmall}`}
                                type="button"
                                onClick={() => {
                                  if (params.tensor_field.grids.length <= 1) {
                                    return;
                                  }
                                  const next = params.tensor_field.grids.filter((_: any, gridIndex: any) => gridIndex !== index);
                                  updateParam(["tensor_field", "grids"], next);
                                }}
                              >
                                {t.removeItem}
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className={paramSection}>
                      <div className={paramSectionHeader}>
                        <h4 className={panelTitleBase}>{t.radials}</h4>
                        <button
                          className={buttonBase}
                          type="button"
                          onClick={() =>
                            updateParam(["tensor_field", "radials"], [
                              ...params.tensor_field.radials,
                              { x: 0, y: 0, size: 55, decay: 5 },
                            ])
                          }
                        >
                          {t.addRadial}
                        </button>
                      </div>
                      <div className={paramCardList}>
                        {params.tensor_field.radials.map((radial: any, index: any) => (
                          <div key={`radial-${index}`} className={paramCard}>
                            <div className={paramCardHeader}>
                              <span>{t.radialItem} {index + 1}</span>
                            </div>
                            <div className={paramCardBody}>
                              <div className={paramRowBase}>
                                <label className={paramItemBase}>
                                  <span className={paramLabelBase}>X</span>
                                  <input
                                    className={paramInputBase}
                                    type="number"
                                    value={radial.x}
                                    onChange={(event) =>
                                      updateParam(["tensor_field", "radials", index, "x"], toNumber(event.target.value, radial.x))
                                    }
                                  />
                                </label>
                                <label className={paramItemBase}>
                                  <span className={paramLabelBase}>Y</span>
                                  <input
                                    className={paramInputBase}
                                    type="number"
                                    value={radial.y}
                                    onChange={(event) =>
                                      updateParam(["tensor_field", "radials", index, "y"], toNumber(event.target.value, radial.y))
                                    }
                                  />
                                </label>
                                <label className={paramItemBase}>
                                  <span className={paramLabelBase}>尺寸</span>
                                  <input
                                    className={paramInputBase}
                                    type="number"
                                    value={radial.size}
                                    onChange={(event) =>
                                      updateParam(["tensor_field", "radials", index, "size"], toNumber(event.target.value, radial.size))
                                    }
                                  />
                                </label>
                                <label className={paramItemBase}>
                                  <span className={paramLabelBase}>衰减</span>
                                  <input
                                    className={paramInputBase}
                                    type="number"
                                    value={radial.decay}
                                    onChange={(event) =>
                                      updateParam(["tensor_field", "radials", index, "decay"], toNumber(event.target.value, radial.decay))
                                    }
                                  />
                                </label>
                              </div>
                              <button
                                className={`${buttonBase} ${buttonSmall}`}
                                type="button"
                                onClick={() => {
                                  if (params.tensor_field.radials.length <= 1) {
                                    return;
                                  }
                                  const next = params.tensor_field.radials.filter((_: any, radialIndex: any) => radialIndex !== index);
                                  updateParam(["tensor_field", "radials"], next);
                                }}
                              >
                                {t.removeItem}
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </details>

                <details className={collapsePanel}>
                  <summary className={collapseTitle}>{t.mapSection}</summary>
                  <div className={collapseBody}>
                    <label className={fieldBase}>
                      <span>{t.animate}</span>
                      <input
                        type="checkbox"
                        checked={params.map.animate}
                        onChange={(event) => updateParam(["map", "animate"], event.target.checked)}
                      />
                    </label>
                    <div className={fieldBase}>
                      <span>{t.animateSpeed}</span>
                      <div className={sliderRowBase}>
                        <input
                          type="range"
                          min="1"
                          max="30"
                          step="1"
                          value={params.map.animate_speed}
                          onChange={(event) =>
                            updateParam(["map", "animate_speed"], toNumber(event.target.value, params.map.animate_speed))
                          }
                        />
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.animate_speed}
                          onChange={(event) =>
                            updateParam(["map", "animate_speed"], toNumber(event.target.value, params.map.animate_speed))
                          }
                        />
                      </div>
                    </div>

                    <h4 className={panelTitleBase}>{t.water}</h4>
                    <div className={fieldBase}>
                      <span>{t.riverBankSize}</span>
                      <input
                        className={inputBase}
                        type="number"
                        value={params.map.water.river_bank_size}
                        onChange={(event) =>
                          updateParam(["map", "water", "river_bank_size"], toNumber(event.target.value, params.map.water.river_bank_size))
                        }
                      />
                    </div>
                    <div className={fieldBase}>
                      <span>{t.riverSize}</span>
                      <input
                        className={inputBase}
                        type="number"
                        value={params.map.water.river_size}
                        onChange={(event) =>
                          updateParam(["map", "water", "river_size"], toNumber(event.target.value, params.map.water.river_size))
                        }
                      />
                    </div>
                    <div className={fieldBase}>
                      <span>{t.coastlineNoise}</span>
                      <div className={paramGridBase}>
                        <label className={paramPairBase}>
                          <span>{t.enabled}</span>
                          <input
                            type="checkbox"
                            checked={params.map.water.coastline.noise_enabled}
                            onChange={(event) =>
                              updateParam(["map", "water", "coastline", "noise_enabled"], event.target.checked)
                            }
                          />
                        </label>
                        <label className={paramPairBase}>
                          <span>{t.noiseSize}</span>
                          <input
                            className={inputBase}
                            type="number"
                            value={params.map.water.coastline.noise_size}
                            onChange={(event) =>
                              updateParam(["map", "water", "coastline", "noise_size"], toNumber(event.target.value, params.map.water.coastline.noise_size))
                            }
                          />
                        </label>
                        <label className={paramPairBase}>
                          <span>{t.noiseAngle}</span>
                          <input
                            className={inputBase}
                            type="number"
                            value={params.map.water.coastline.noise_angle}
                            onChange={(event) =>
                              updateParam(["map", "water", "coastline", "noise_angle"], toNumber(event.target.value, params.map.water.coastline.noise_angle))
                            }
                          />
                        </label>
                      </div>
                    </div>
                    <div className={fieldBase}>
                      <span>{t.coastlineWidth}</span>
                      <input
                        className={inputBase}
                        type="number"
                        value={params.map.water.coastline_width}
                        onChange={(event) =>
                          updateParam(["map", "water", "coastline_width"], toNumber(event.target.value, params.map.water.coastline_width))
                        }
                      />
                    </div>
                    <div className={fieldBase}>
                      <span>{t.riverNoise}</span>
                      <div className={paramGridBase}>
                        <label className={paramPairBase}>
                          <span>{t.enabled}</span>
                          <input
                            type="checkbox"
                            checked={params.map.water.river.noise_enabled}
                            onChange={(event) =>
                              updateParam(["map", "water", "river", "noise_enabled"], event.target.checked)
                            }
                          />
                        </label>
                        <label className={paramPairBase}>
                          <span>{t.noiseSize}</span>
                          <input
                            className={inputBase}
                            type="number"
                            value={params.map.water.river.noise_size}
                            onChange={(event) =>
                              updateParam(["map", "water", "river", "noise_size"], toNumber(event.target.value, params.map.water.river.noise_size))
                            }
                          />
                        </label>
                        <label className={paramPairBase}>
                          <span>{t.noiseAngle}</span>
                          <input
                            className={inputBase}
                            type="number"
                            value={params.map.water.river.noise_angle}
                            onChange={(event) =>
                              updateParam(["map", "water", "river", "noise_angle"], toNumber(event.target.value, params.map.water.river.noise_angle))
                            }
                          />
                        </label>
                      </div>
                    </div>
                    <div className={fieldBase}>
                      <span>{t.simplifyTolerance}</span>
                      <div className={sliderRowBase}>
                        <input
                          type="range"
                          min="0"
                          max="2"
                          step="0.1"
                          value={params.map.water.simplify_tolerance}
                          onChange={(event) =>
                            updateParam(["map", "water", "simplify_tolerance"], toNumber(event.target.value, params.map.water.simplify_tolerance))
                          }
                        />
                        <input
                          className={inputBase}
                          type="number"
                          step="0.1"
                          value={params.map.water.simplify_tolerance}
                          onChange={(event) =>
                            updateParam(["map", "water", "simplify_tolerance"], toNumber(event.target.value, params.map.water.simplify_tolerance))
                          }
                        />
                      </div>
                    </div>
                    <h4 className={panelTitleBase}>{t.waterDevParams}</h4>
                    <div className={paramGridBase}>
                      <label className={paramPairBase}>
                        <span>{t.devSep}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.water.dev_params.dsep}
                          onChange={(event) =>
                            updateParam(["map", "water", "dev_params", "dsep"], toNumber(event.target.value, params.map.water.dev_params.dsep))
                          }
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.devTest}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.water.dev_params.dtest}
                          onChange={(event) =>
                            updateParam(["map", "water", "dev_params", "dtest"], toNumber(event.target.value, params.map.water.dev_params.dtest))
                          }
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.devPath}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.water.dev_params.path_iterations}
                          onChange={(event) =>
                            updateParam(["map", "water", "dev_params", "path_iterations"], toNumber(event.target.value, params.map.water.dev_params.path_iterations))
                          }
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.devSeed}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.water.dev_params.seed_tries}
                          onChange={(event) =>
                            updateParam(["map", "water", "dev_params", "seed_tries"], toNumber(event.target.value, params.map.water.dev_params.seed_tries))
                          }
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.devStep}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.water.dev_params.dstep}
                          onChange={(event) =>
                            updateParam(["map", "water", "dev_params", "dstep"], toNumber(event.target.value, params.map.water.dev_params.dstep))
                          }
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.devLookahead}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.water.dev_params.dlookahead}
                          onChange={(event) =>
                            updateParam(["map", "water", "dev_params", "dlookahead"], toNumber(event.target.value, params.map.water.dev_params.dlookahead))
                          }
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.devCircleJoin}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.water.dev_params.dcircle_join}
                          onChange={(event) =>
                            updateParam(["map", "water", "dev_params", "dcircle_join"], toNumber(event.target.value, params.map.water.dev_params.dcircle_join))
                          }
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.devJoinAngle}</span>
                        <input
                          className={inputBase}
                          type="number"
                          step="0.1"
                          value={params.map.water.dev_params.join_angle}
                          onChange={(event) =>
                            updateParam(["map", "water", "dev_params", "join_angle"], toNumber(event.target.value, params.map.water.dev_params.join_angle))
                          }
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.devSimplify}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.water.simplify_tolerance}
                          onChange={(event) =>
                            updateParam(["map", "water", "dev_params", "simplify_tolerance"], toNumber(event.target.value, params.map.water.simplify_tolerance))
                          }
                        />
                      </label>
                    </div>

                    <h4 className={panelTitleBase}>{t.roads}</h4>
                    {(["main", "major", "minor"] as const).map((roadKey) => (
                      <div key={roadKey} className={panelBase}>
                        <h4 className={panelTitleBase}>{roadLabels[roadKey]}</h4>
                        <div className={paramGridBase}>
                          <label className={paramPairBase}>
                            <span>{t.devSep}</span>
                            <input
                              className={inputBase}
                              type="number"
                              value={params.map[roadKey].dsep}
                              onChange={(event) =>
                                updateParam(["map", roadKey, "dsep"], toNumber(event.target.value, params.map[roadKey].dsep))
                              }
                            />
                          </label>
                          <label className={paramPairBase}>
                            <span>{t.devTest}</span>
                            <input
                              className={inputBase}
                              type="number"
                              value={params.map[roadKey].dtest}
                              onChange={(event) =>
                                updateParam(["map", roadKey, "dtest"], toNumber(event.target.value, params.map[roadKey].dtest))
                              }
                            />
                          </label>
                          <label className={paramPairBase}>
                            <span>{t.devPath}</span>
                            <input
                              className={inputBase}
                              type="number"
                              value={params.map[roadKey].dev_params.path_iterations}
                              onChange={(event) =>
                                updateParam(["map", roadKey, "dev_params", "path_iterations"], toNumber(event.target.value, params.map[roadKey].dev_params.path_iterations))
                              }
                            />
                          </label>
                          <label className={paramPairBase}>
                            <span>{t.devSeed}</span>
                            <input
                              className={inputBase}
                              type="number"
                              value={params.map[roadKey].dev_params.seed_tries}
                              onChange={(event) =>
                                updateParam(["map", roadKey, "dev_params", "seed_tries"], toNumber(event.target.value, params.map[roadKey].dev_params.seed_tries))
                              }
                            />
                          </label>
                        </div>
                        <div className={paramGridBase}>
                          <label className={paramPairBase}>
                            <span>{t.devStep}</span>
                            <input
                              className={inputBase}
                              type="number"
                              value={params.map[roadKey].dev_params.dstep}
                              onChange={(event) =>
                                updateParam(["map", roadKey, "dev_params", "dstep"], toNumber(event.target.value, params.map[roadKey].dev_params.dstep))
                              }
                            />
                          </label>
                          <label className={paramPairBase}>
                            <span>{t.devLookahead}</span>
                            <input
                              className={inputBase}
                              type="number"
                              value={params.map[roadKey].dev_params.dlookahead}
                              onChange={(event) =>
                                updateParam(["map", roadKey, "dev_params", "dlookahead"], toNumber(event.target.value, params.map[roadKey].dev_params.dlookahead))
                              }
                            />
                          </label>
                          <label className={paramPairBase}>
                            <span>{t.devCircleJoin}</span>
                            <input
                              className={inputBase}
                              type="number"
                              value={params.map[roadKey].dev_params.dcircle_join}
                              onChange={(event) =>
                                updateParam(["map", roadKey, "dev_params", "dcircle_join"], toNumber(event.target.value, params.map[roadKey].dev_params.dcircle_join))
                              }
                            />
                          </label>
                          <label className={paramPairBase}>
                            <span>{t.devJoinAngle}</span>
                            <input
                              className={inputBase}
                              type="number"
                              step="0.1"
                              value={params.map[roadKey].dev_params.join_angle}
                              onChange={(event) =>
                                updateParam(["map", roadKey, "dev_params", "join_angle"], toNumber(event.target.value, params.map[roadKey].dev_params.join_angle))
                              }
                            />
                          </label>
                          <label className={paramPairBase}>
                            <span>{t.devSimplify}</span>
                            <input
                              className={inputBase}
                              type="number"
                              step="0.1"
                              value={params.map[roadKey].dev_params.simplify_tolerance}
                              onChange={(event) =>
                                updateParam(["map", roadKey, "dev_params", "simplify_tolerance"], toNumber(event.target.value, params.map[roadKey].dev_params.simplify_tolerance))
                              }
                            />
                          </label>
                          <label className={paramPairBase}>
                            <span>{t.devCollide}</span>
                            <input
                              className={inputBase}
                              type="number"
                              value={params.map[roadKey].dev_params.collide_early}
                              onChange={(event) =>
                                updateParam(["map", roadKey, "dev_params", "collide_early"], toNumber(event.target.value, params.map[roadKey].dev_params.collide_early))
                              }
                            />
                          </label>
                        </div>
                      </div>
                    ))}

                    <h4 className={panelTitleBase}>{t.parks}</h4>
                    <div className={paramGridBase}>
                      <label className={paramPairBase}>
                        <span>{t.clusterBigParks}</span>
                        <input
                          type="checkbox"
                          checked={params.map.parks.cluster_big_parks}
                          onChange={(event) => updateParam(["map", "parks", "cluster_big_parks"], event.target.checked)}
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.parkBigCount}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.parks.num_big_parks}
                          onChange={(event) =>
                            updateParam(["map", "parks", "num_big_parks"], toNumber(event.target.value, params.map.parks.num_big_parks))
                          }
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.parkSmallCount}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.parks.num_small_parks}
                          onChange={(event) =>
                            updateParam(["map", "parks", "num_small_parks"], toNumber(event.target.value, params.map.parks.num_small_parks))
                          }
                        />
                      </label>
                    </div>

                    <h4 className={panelTitleBase}>{t.buildings}</h4>
                    <div className={paramGridBase}>
                      <label className={paramPairBase}>
                        <span>{t.buildingMinArea}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.buildings.min_area}
                          onChange={(event) =>
                            updateParam(["map", "buildings", "min_area"], toNumber(event.target.value, params.map.buildings.min_area))
                          }
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.buildingMaxLength}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.buildings.max_length}
                          onChange={(event) =>
                            updateParam(["map", "buildings", "max_length"], toNumber(event.target.value, params.map.buildings.max_length))
                          }
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.buildingShrinkSpacing}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.map.buildings.shrink_spacing}
                          onChange={(event) =>
                            updateParam(["map", "buildings", "shrink_spacing"], toNumber(event.target.value, params.map.buildings.shrink_spacing))
                          }
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.buildingNoDivide}</span>
                        <input
                          className={inputBase}
                          type="number"
                          step="0.01"
                          value={params.map.buildings.chance_no_divide}
                          onChange={(event) =>
                            updateParam(["map", "buildings", "chance_no_divide"], toNumber(event.target.value, params.map.buildings.chance_no_divide))
                          }
                        />
                      </label>
                    </div>
                  </div>
                </details>

                <details className={collapsePanel}>
                  <summary className={collapseTitle}>{t.style}</summary>
                  <div className={collapseBody}>
                    <label className={fieldBase}>
                      <span>{t.colourScheme}</span>
                      <input
                        className={inputBase}
                        value={params.style.colour_scheme}
                        onChange={(event) => updateParam(["style", "colour_scheme"], event.target.value)}
                      />
                    </label>
                    <div className={paramGridBase}>
                      <label className={paramPairBase}>
                        <span>{t.zoomBuildings}</span>
                        <input
                          type="checkbox"
                          checked={params.style.zoom_buildings}
                          onChange={(event) => updateParam(["style", "zoom_buildings"], event.target.checked)}
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.buildingModels}</span>
                        <input
                          type="checkbox"
                          checked={params.style.building_models}
                          onChange={(event) => updateParam(["style", "building_models"], event.target.checked)}
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.showFrame}</span>
                        <input
                          type="checkbox"
                          checked={params.style.show_frame}
                          onChange={(event) => updateParam(["style", "show_frame"], event.target.checked)}
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.orthographic}</span>
                        <input
                          type="checkbox"
                          checked={params.style.orthographic}
                          onChange={(event) => updateParam(["style", "orthographic"], event.target.checked)}
                        />
                      </label>
                    </div>
                    <div className={buttonRowBase}>
                      <input
                        className={inputBase}
                        type="number"
                        value={params.style.camera_x}
                        onChange={(event) => updateParam(["style", "camera_x"], toNumber(event.target.value, params.style.camera_x))}
                      />
                      <input
                        className={inputBase}
                        type="number"
                        value={params.style.camera_y}
                        onChange={(event) => updateParam(["style", "camera_y"], toNumber(event.target.value, params.style.camera_y))}
                      />
                    </div>
                  </div>
                </details>

                <details className={collapsePanel}>
                  <summary className={collapseTitle}>{t.options}</summary>
                  <div className={collapseBody}>
                    <label className={fieldBase}>
                      <span>{t.drawCenter}</span>
                      <input
                        type="checkbox"
                        checked={params.options.draw_center}
                        onChange={(event) => updateParam(["options", "draw_center"], event.target.checked)}
                      />
                    </label>
                    <label className={fieldBase}>
                      <span>{t.highDpi}</span>
                      <input
                        type="checkbox"
                        checked={params.options.high_dpi}
                        onChange={(event) => updateParam(["options", "high_dpi"], event.target.checked)}
                      />
                    </label>
                  </div>
                </details>

                <details className={collapsePanel}>
                  <summary className={collapseTitle}>{t.download}</summary>
                  <div className={collapseBody}>
                    <label className={fieldBase}>
                      <span>{t.imageScale}</span>
                      <input
                        className={inputBase}
                        type="number"
                        value={params.download.image_scale}
                        onChange={(event) => updateParam(["download", "image_scale"], toNumber(event.target.value, params.download.image_scale))}
                      />
                    </label>
                    <label className={fieldBase}>
                      <span>{t.typeLabel}</span>
                      <input
                        className={inputBase}
                        value={params.download.type}
                        onChange={(event) => updateParam(["download", "type"], event.target.value)}
                      />
                    </label>
                  </div>
                </details>

                <details className={collapsePanel}>
                  <summary className={collapseTitle}>{t.parkPolygons}</summary>
                  <div className={collapseBody}>
                    <div className={paramGridBase}>
                      <label className={paramPairBase}>
                        <span>{t.polygonMaxLength}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.park_polygons.max_length}
                          onChange={(event) => updateParam(["park_polygons", "max_length"], toNumber(event.target.value, params.park_polygons.max_length))}
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.polygonMinArea}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.park_polygons.min_area}
                          onChange={(event) => updateParam(["park_polygons", "min_area"], toNumber(event.target.value, params.park_polygons.min_area))}
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.polygonShrinkSpacing}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.park_polygons.shrink_spacing}
                          onChange={(event) => updateParam(["park_polygons", "shrink_spacing"], toNumber(event.target.value, params.park_polygons.shrink_spacing))}
                        />
                      </label>
                      <label className={paramPairBase}>
                        <span>{t.polygonNoDivide}</span>
                        <input
                          className={inputBase}
                          type="number"
                          value={params.park_polygons.chance_no_divide}
                          onChange={(event) => updateParam(["park_polygons", "chance_no_divide"], toNumber(event.target.value, params.park_polygons.chance_no_divide))}
                        />
                      </label>
                    </div>
                  </div>
                </details>

                  <div >
                    <div className="mt-1 mb-1 grid grid-cols-3 gap-2">
                    <button
                      className={`${buttonBase} ${buttonGhost}`}
                      type="button"
                      onClick={() => setParams(templateParams)}
                    >
                      {t.resetTemplate}
                    </button>
                    <button
                      className={`${buttonBase} ${buttonGhost}`}
                      onClick={handleGenerate}
                      disabled={isGenerating}
                    >
                      {t.generateLayout}
                    </button>
                    <button
                      className={`${buttonBase} ${buttonGhost}`}
                      onClick={handleSave}
                    >
                      {t.saveSvg}
                    </button>
                  </div>
                    {status ? <p className={statusText}>{status}</p> : null}
                    {error ? <p className={errorText}>{error}</p> : null}
                  </div>
                </div>
              </div>
            </div>

            <div className={workspaceFrame}>
              <div className={workspacePreviewPane}>
                <div className={tabHeader}>
                <button
                  className={`${tabButtonBase} ${activeTab === "preview" ? tabButtonActive : ""}`}
                  type="button"
                  onClick={() => setActiveTab("preview")}
                >
                  {t.preview}
                </button>
                <button
                  className={`${tabButtonBase} ${activeTab === "editor" ? tabButtonActive : ""}`}
                  type="button"
                  onClick={() => setActiveTab("editor")}
                >
                  {t.editor}
                </button>
                <button
                  className={`${tabButtonBase} ${activeTab === "library" ? tabButtonActive : ""}`}
                  type="button"
                  onClick={() => setActiveTab("library")}
                >
                  {t.library}
                </button>
                <button
                  className={`${tabButtonBase} ${activeTab === "artifacts" ? tabButtonActive : ""}`}
                  type="button"
                  onClick={() => setActiveTab("artifacts")}
                >
                  {t.artifacts}
                </button>
              </div>

                {activeTab === "preview" && (
                  <div className={`${tabPanelScroll} flex flex-col`} id="layout-preview">
                  <div className={panelHeaderBase}>
                    <div className={metaBase}>
                      <LayoutSelector
                        className={layoutSelectBase}
                        selectClassName={inputBase}
                        value={layout_id ?? ""}
                        layouts={layouts}
                        emptyLabel={t.layoutSelect}
                        optionPrefix={t.listPrefix}
                        onChange={handleLayoutSelect}
                      />
                      {/*<span>{t.layout_id}: {layout_id ?? "-"}</span>*/}
                      {/*<span>{t.mode}: {responseModeLabel}</span>*/}
                    </div>
                  </div>
                  <div className="flex-1 min-h-0 mt-4">
                    <SvgPreview svgUrl={resolvePreviewUrl(svgUrl)} />
                  </div>
                </div>
              )}

                {activeTab === "editor" && (
                  <div className={`${tabPanelScroll} flex flex-col`} id="layout-editor">
                  <div className={panelHeaderBase}>
                    <div className={metaBase}>
                      <LayoutSelector
                        className={layoutSelectBase}
                        selectClassName={inputBase}
                        value={layout_id ?? ""}
                        layouts={layouts}
                        emptyLabel={t.layoutSelect}
                        optionPrefix={t.listPrefix}
                        onChange={handleLayoutSelect}
                      />
                      {/*<span>{t.sourceLabel}: {svg_content ? t.svgSourceInline : svgUrl ? t.svgSourceUrl : t.svgSourceEmpty}</span>*/}
                    </div>
                  </div>
                  <div className="flex-1 min-h-0 mt-4">
                    <SvgTextEditor svgUrl={svgUrl} />
                  </div>
                </div>
              )}

                {activeTab === "library" && (
                  <div className={`${tabPanelClip} flex h-full min-h-0 flex-col overflow-hidden`}>
                  <div className="pretty-scrollbar flex-1 h-0 min-h-0 overflow-y-auto overflow-x-hidden overscroll-contain">
                    <LayoutList
                      layouts={layouts.map((l) => ({
                        layout_id: l.layout_id,
                        svg_url: l.svg_url,
                        status: l.status,
                        layout_name: l.layout_name,
                      }))}
                      labels={layoutListLabels}
                      onEdit={handleEditLayout}
                      onGenerateModel={handleGenerateModel}
                      onDelete={handleDelete}
                      onLoad={handleLoadFromLibrary}
                    />
                  </div>
                </div>
              )}

                {activeTab === "artifacts" && (
                  <div className={tabPanelScroll} id="layout-artifacts">
                  <ArtifactsEditor
                    mode="polygons"
                    data={artifactsData}
                    showOverview
                    labels={artifactsLabels}
                    onChange={setArtifactsData}
                    onSaveArtifacts={handleSaveArtifacts}
                    layoutSelector={
                      <LayoutSelector
                        className={`${layoutSelectBase} flex-shrink-0`}
                        selectClassName={`${inputBase} flex-shrink-0`}
                        value={artifactsLayoutId ?? layout_id ?? ""}
                        layouts={layouts}
                        emptyLabel={t.layoutSelect}
                        optionPrefix={t.listPrefix}
                        onChange={handleArtifactsLayoutSelect}
                      />
                    }
                    saveArtifactsLabel={t.saveArtifacts}
                  />
                  </div>
                )}

              </div>
            </div>
          </div>

          {artifactsStatus ? (
            <div className="pointer-events-none fixed inset-x-0 top-4 z-50 flex justify-center px-4">
              <div
                className={`rounded-lg border px-3 py-2 text-sm shadow-md ${
                  artifactsStatus.includes("失败")
                    ? "border-red-300 bg-red-50 text-red-700"
                    : artifactsStatus.includes("已保存") || artifactsStatus.includes("已提交保存")
                      ? "border-emerald-300 bg-emerald-50 text-emerald-700"
                      : "border-amber-300 bg-amber-50 text-amber-700"
                }`}
              >
                {artifactsStatus}
              </div>
            </div>
          ) : null}

          {isGenerating ? (
            <div className={floatPanel}>
              <div className={floatHeader}>
                <h3 className={floatTitle}>生成状态</h3>
              </div>
              <div className={fieldBase}>
                <span>{phase || "空闲"}</span>
                <div className={progressBar}>
                  <div className={progressFill} style={{ width: `${progress}%` }} />
                </div>
              </div>
              <h3 className={floatTitle}>生成日志</h3>
              {logLines.length === 0 ? (
                <p className="text-[12px] text-[var(--muted)]">暂无日志。</p>
              ) : (
                <div className={listBase}>
                  {logLines.map((line, index) => (
                    <div key={`${line}-${index}`} className={listItemBase}>
                      <span>{line}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>

      {/* 新增：SVG可视化编辑器对话框 */}
      <SvgEditorModal
        onSave={handleSaveEditedSvg}
        onGenerateModel={() => {
          if (editinglayout_id) {
            handleGenerateModel(editinglayout_id);
          }
        }}
      />
    </section>
  );
}

