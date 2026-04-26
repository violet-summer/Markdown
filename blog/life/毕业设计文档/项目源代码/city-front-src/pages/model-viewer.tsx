import { useEffect, useMemo, useRef, useState } from "react";
import { generateModel, getModelFile, getModelProgress, getModelResult, listModels } from "../api/model";
import { ModelViewer } from "@/components/scene/ModelViewer";
import type { ApiEnvelope } from "../models/api-contract";
import { useUiLanguage } from "../utils/ui";
import { GenerateModelProgressResponse, GenerateModelResponse, LayoutWithModels, ModelListResponseDTO, ModelResultResponse } from "@/models/model-api";
import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { setLayoutCityGlbModelIds } from "@/store/city-glb-download-slice";
import { setLayoutWithModels, setModelFileById } from "@/store/model-viewer-data-slice";

// 新响应结构类型定义
export interface Response {
    model?: ModelFileInfo;
    status?: number;
    [property: string]: any;
}

export interface ModelFileInfo {
    model_id?: string;
    presigned_url?: string;
    [property: string]: any;
}

export function ModelViewerPage() {
  const dispatch = useAppDispatch();
  const cityGlbModelIdsByLayout = useAppSelector((state) => state.cityGlbDownload.modelIdsByLayout);
  const layoutWithModels = useAppSelector((state) => state.modelViewerData.layoutWithModels);
  const modelFilesById = useAppSelector((state) => state.modelViewerData.modelFilesById);
  const language = useUiLanguage();
  const t = language === "zh" ? {
    generateTitle: "生成模型",
    layout_id: "布局 ID",
    layoutSelect: "布局选择",
    modelSelect: "模型选择",
    generateButton: "生成模型",
    statusGenerating: "正在生成模型...",
    statusStarting: "模型任务已启动...",
    statusBuilding: "模型生成中...",
    statusDone: "模型生成结束，正在获取结果...",
    statusLoadingModel: "正在加载模型文件...",
    statusReady: "模型已就绪。",
    errorAuth: "需要登录，请先登录。",
    errorGenerate: "生成失败。",
    errorNoModel: "当前布局下暂无可预览模型。",
    previewTitle: "3D 预览",
    objReady: "就绪",
    mtlReady: "就绪",
    modelsTitle: "布局与模型",
    total: "布局数量",
    empty: "暂无布局模型数据。",
    modelCount: "模型数",
    downloadLayoutModels: "下载当前布局模型",
    statusDownloading: "正在准备下载模型...",
    statusDownloadReady: "下载已触发",
    errorNoDownloadModel: "当前布局下暂无可下载的 city.glb 模型。",
  } : {
    generateTitle: "Generate Model",
    layout_id: "Layout ID",
    layoutSelect: "Layout",
    modelSelect: "Model",
    responseMode: "Response mode",
    responseInline: "inline",
    generateButton: "Generate model",
    statusGenerating: "Generating model...",
    statusStarting: "Generation started...",
    statusBuilding: "Model building...",
    statusDone: "Generation done, fetching result...",
    statusLoadingModel: "Loading model file...",
    statusReady: "Model ready.",
    errorAuth: "Auth token required. Please log in first.",
    errorGenerate: "Model generation failed.",
    errorNoModel: "No model available under this layout.",
    previewTitle: "3D Preview",
    objReady: "ready",
    mtlReady: "ready",
    modelsTitle: "Layouts & Models",
    total: "Layouts",
    empty: "No layout model data yet.",
    modelCount: "Model count",
    downloadLayoutModels: "Download layout models",
    statusDownloading: "Preparing model download...",
    statusDownloadReady: "Download triggered",
    errorNoDownloadModel: "No downloadable city.glb model under this layout.",
  };
  const [layout_id, setlayout_id] = useState("1");
  const [responseMode, setResponseMode] = useState<"url" | "inline">("url");
  const [objContents, setObjContents] = useState<string[]>([]);
  const [glbUrls, setGlbUrls] = useState<string[]>([]);
  const [selectedLayoutId, setSelectedLayoutId] = useState("");
  const [selectedModelId, setSelectedModelId] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const modelCacheRef = useRef<Record<string, ModelFileInfo>>({});
  const buttonBase = "rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-2.5 py-1.5 text-[12px] font-semibold transition-all duration-150 hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-16px_var(--shadow)] disabled:cursor-not-allowed disabled:opacity-60";
  const buttonPrimary = "border-transparent bg-[var(--accent)] text-white";
  const buttonSmall = "px-3";
  const panelBase = "min-w-0 w-full max-w-full rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-2 py-3 shadow-[0_12px_24px_-22px_var(--shadow)]";
  const fieldBase = "flex items-center gap-1.5 text-[12px] text-[var(--muted)]";
  const inputBase = "rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2 py-1.5 text-[12px] text-[var(--ink)]";
  const workspaceShell = "grid gap-3 h-full min-h-0 overflow-hidden";
  const workspaceBody = "grid grid-cols-1 gap-3 h-full min-h-0";
  const workspaceMain = "min-h-0 h-full";
  const workspaceColumns = "grid h-full min-h-0 min-w-0 gap-3 lg:grid-cols-[minmax(0,clamp(280px,24vw,340px))_minmax(0,1fr)]";
  const workspacePane = "flex h-full min-h-0 min-w-0 max-h-full w-full max-w-full flex-col";
  const metaBase = "flex flex-wrap items-center gap-2 text-[12px] text-[var(--muted)]";
  const listBase = "flex w-full min-w-0 flex-col gap-1";
  const listItemBase = "flex w-full min-w-0 max-w-full box-border items-center justify-between gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface-2)] px-0.5 py-1.5 text-[12px] min-h-10";
  const listItemInteractive = "cursor-pointer transition-colors hover:bg-[var(--surface)]";
  const listItemSelected = "border-[var(--accent)] bg-[var(--surface)]";
  const listMeta = "text-[11px] text-[var(--muted)]";
  const statusText = "mt-2 text-[12px] text-[var(--accent-2)]";
  const errorText = "mt-2 text-[12px] text-[#8a2f2f]";

  const unwrapPayload = <T,>(payload: ApiEnvelope<T> | T | null | undefined): T | null => {
    if (!payload || typeof payload !== "object") return null;
    if ("data" in payload) {
      return ((payload as ApiEnvelope<T>).data ?? null) as T | null;
    }
    return payload as T;
  };

  const readObjContent = (file: ModelFileInfo | undefined) => {
    if (!file) return "";
    return file.objContent ?? "";
  };

  const isCityGlbUrl = (url: string) => url.toLowerCase().includes("city.glb");
  const isRenderableGlbUrl = (url: string) => url.toLowerCase().includes(".glb") && !isCityGlbUrl(url);

  const readModelFromResponse = (response: unknown): ModelFileInfo | undefined => {
    const data = (response && typeof response === "object" && "model" in (response as any)) ? (response as any) : {};
    return data.model as ModelFileInfo | undefined;
  };

  const rememberCityGlbModelIds = (layoutId: string, entries: Array<{ modelId: string; file: ModelFileInfo }>) => {
    if (!layoutId) return;
    const ids = Array.from(
      new Set(
        entries
          .filter((entry) => isCityGlbUrl(entry.file?.presigned_url ?? ""))
          .map((entry) => entry.modelId)
          .filter((id): id is string => Boolean(id))
      )
    );
    dispatch(setLayoutCityGlbModelIds({ layoutId, modelIds: ids }));
  };

  const applyModelFiles = (files: ModelFileInfo[]) => {
    const glbList = files
      .map((file) => file?.presigned_url ?? "")
      .filter((url): url is string => Boolean(url) && isRenderableGlbUrl(url));

    setGlbUrls(glbList);

    const contents = files
      .map((file) => readObjContent(file))
      .filter((content): content is string => Boolean(content));

    if (glbList.length === 0 && contents.length === 0) {
      setObjContents([]);
      throw new Error(t.errorNoModel);
    }

    setObjContents(contents);
  };

  const loadModelFileById = async (modelId: string) => {
    const response = await getModelFile(modelId);
    console.log(`/api/models/model/${modelId} 响应:`, response);
    const model: ModelFileInfo | undefined = readModelFromResponse(response);
    if (model && model.presigned_url) {
      const url = model.presigned_url;
      const lowerUrl = url.toLowerCase();
      if (lowerUrl.includes('.obj')) {
        try {
         
          const res = await fetch(url);
          if (!res.ok) throw new Error("模型文件下载失败");
          const objText = await res.text();
          model.objContent = objText;
        } catch (e) {
          setError("模型文件下载失败");
          model.objContent = "";
        }
      } else if (lowerUrl.includes('.glb')) {
        // GLB 文件无需下载内容，直接用 URL
         // 获取实际的glb模型文件内容，供OBJLoader使用
        model.objContent = "";
      }
    }
    if (model) {
      modelCacheRef.current[modelId] = model;
      dispatch(setModelFileById({ modelId, file: model }));
    }
    return model;
  };

  const fetchModelFilesSequentially = async (modelIds: string[]) => {
    const available: Array<{ modelId: string; file: ModelFileInfo }> = [];

    for (const modelId of modelIds) {
      if (!modelId) continue;

      const cached = modelCacheRef.current[modelId] ?? modelFilesById[modelId];
      if (cached) {
        available.push({ modelId, file: cached });
        continue;
      }

      try {
        setStatus(`${t.statusLoadingModel} (${modelId})`);
        // eslint-disable-next-line no-await-in-loop
        const file = await loadModelFileById(modelId);
        if (file) {
          available.push({ modelId, file });
        }
      } catch {
        // 忽略单个模型失败，继续尝试下一个
      }
    }

    return available;
  };

  const selectedLayout = useMemo(
    () => layoutWithModels.find((item) => item.layout?.layout_id === selectedLayoutId),
    [layoutWithModels, selectedLayoutId],
  );
  const selectedLayoutModels = (selectedLayout?.models ?? []) as ModelListResponseDTO[];

  const refreshLayoutModels = async (preferredLayoutId?: string) => {
    const response = await listModels();
    console.log("/api/models/list 响应:", response);
    let nextList: LayoutWithModels[] = [];
    if (response && typeof response === "object" && Array.isArray((response as any).layout_with_models_list)) {
      nextList = (response as any).layout_with_models_list;
    }
    dispatch(setLayoutWithModels(nextList));

    if (nextList.length === 0) {
      setSelectedLayoutId("");
      setSelectedModelId("");
      setObjContents([]);
      setGlbUrls([]);
      return;
    }

    const resolvedLayoutId =
      preferredLayoutId && nextList.some((item) => item.layout?.layout_id === preferredLayoutId)
        ? preferredLayoutId
        : (nextList[0].layout?.layout_id ?? "");

    setSelectedLayoutId(resolvedLayoutId);
    setlayout_id(resolvedLayoutId || layout_id);

    const firstLayout = nextList.find((item) => item.layout?.layout_id === resolvedLayoutId) ?? nextList[0];
    const modelIds = (firstLayout?.models ?? [])
      .map((model) => model?.model_id ?? "")
      .filter((value): value is string => Boolean(value));

    if (modelIds.length === 0) {
      setSelectedModelId("");
      setObjContents([]);
      setGlbUrls([]);
      setStatus("");
      return;
    }

    const available = await fetchModelFilesSequentially(modelIds);
    rememberCityGlbModelIds(resolvedLayoutId, available);
    if (available.length > 0) {
      setSelectedModelId(available[0].modelId);
      applyModelFiles(available.map((item) => item.file));
      setStatus(t.statusReady);
    } else {
      setSelectedModelId(modelIds[0]);
      setObjContents([]);
      setStatus("");
      setError(t.errorNoModel);
    }
  };

  useEffect(() => {
    void refreshLayoutModels();
    return () => undefined;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleGenerate = async () => {
    setError("");
    const token = window.localStorage.getItem("auth_token") ?? "";
    if (!token) {
      setError(t.errorAuth);
      return;
    }
    try {
      setStatus(t.statusGenerating);
      const kickoff = (await generateModel({
        // 开发实际开发阶段不要使用数值化返回
        layout_id: layout_id,
        response_mode: responseMode,
      })) as ApiEnvelope<GenerateModelResponse> | GenerateModelResponse;

      const kickoffData =
        kickoff && typeof kickoff === "object" && "data" in kickoff
          ? ((kickoff as ApiEnvelope<GenerateModelResponse>).data ?? {})
          : (kickoff as GenerateModelResponse);

      if (typeof kickoffData?.status === "number" && kickoffData.status < 0) {
        throw new Error(kickoffData.message || t.errorGenerate);
      }

      const statusTextMap: Record<number, string> = {
        10: t.statusStarting,
        80: t.statusBuilding,
        100: t.statusDone,
      };

      let completed = false;
      for (let attempt = 0; attempt < 120; attempt += 1) {
        const progress = (await getModelProgress(layout_id)) as ApiEnvelope<GenerateModelProgressResponse> | GenerateModelProgressResponse;
        const progressData =
          progress && typeof progress === "object" && "data" in progress
            ? ((progress as ApiEnvelope<GenerateModelProgressResponse>).data ?? {})
            : (progress as GenerateModelProgressResponse);

        const progressStatus = Number(progressData?.status);
        if (Number.isFinite(progressStatus)) {
          setStatus(statusTextMap[progressStatus] ?? `${t.statusGenerating} (${progressStatus})`);
        }

        if (progressStatus === 100) {
          completed = true;
          break;
        }

        if (progressStatus < 0) {
          throw new Error(progressData?.message || t.errorGenerate);
        }

        // eslint-disable-next-line no-await-in-loop
        await new Promise((resolve) => setTimeout(resolve, 800));
      }

      if (!completed) {
        throw new Error(t.errorGenerate);
      }

      const result = (await getModelResult(layout_id)) as ApiEnvelope<ModelResultResponse> | ModelResultResponse;
      const resultData = unwrapPayload<ModelResultResponse>(result) ?? {};
      const firstModel = Array.isArray(resultData.models) ? resultData.models[0] : undefined;

      if (!firstModel) {
        throw new Error(t.errorGenerate);
      }

      applyModelFiles([firstModel]);
      if (firstModel.modelId) {
        setSelectedModelId(firstModel.modelId);
        dispatch(setModelFileById({ modelId: firstModel.modelId as string, file: firstModel }));
      }
      setStatus(t.statusReady);
      await refreshLayoutModels(layout_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : t.errorGenerate);
      setStatus("");
    }
  };

  const handleLayoutChange = async (nextLayoutId: string) => {
    setError("");
    setSelectedLayoutId(nextLayoutId);
    setlayout_id(nextLayoutId);

    const targetLayout = layoutWithModels.find((item) => item.layout?.layout_id === nextLayoutId);
    const modelIds = (targetLayout?.models ?? [])
      .map((model) => model?.model_id ?? "")
      .filter((value): value is string => Boolean(value));

    if (modelIds.length === 0) {
      setSelectedModelId("");
      setObjContents([]);
      setGlbUrls([]);
      dispatch(setLayoutCityGlbModelIds({ layoutId: nextLayoutId, modelIds: [] }));
      setStatus("");
      setError(t.errorNoModel);
      return;
    }

    try {
      const available = await fetchModelFilesSequentially(modelIds);
      rememberCityGlbModelIds(nextLayoutId, available);
      if (available.length === 0) {
        setSelectedModelId(modelIds[0]);
        setObjContents([]);
        setGlbUrls([]);
        setStatus("");
        setError(t.errorNoModel);
        return;
      }

      setSelectedModelId(available[0].modelId);
      applyModelFiles(available.map((item) => item.file));
      setStatus(t.statusReady);
    } catch (err) {
      setError(err instanceof Error ? err.message : t.errorGenerate);
      setStatus("");
    }
  };

  const handleModelChange = async (modelId: string) => {
    if (!modelId) return;
    setError("");
    setSelectedModelId(modelId);
    try {
      const targetLayout = layoutWithModels.find((item) => item.layout?.layout_id === selectedLayoutId);
      const modelIds = (targetLayout?.models ?? [])
        .map((model) => model?.model_id ?? "")
        .filter((value): value is string => Boolean(value));
      const available = await fetchModelFilesSequentially(modelIds);
      rememberCityGlbModelIds(selectedLayoutId, available);
      applyModelFiles(available.map((item) => item.file));
      setStatus(t.statusReady);
    } catch (err) {
      setError(err instanceof Error ? err.message : t.errorGenerate);
      setStatus("");
    }
  };

  const handleDownloadLayoutModels = async () => {
    setError("");
    const targetLayout = layoutWithModels.find((item) => item.layout?.layout_id === selectedLayoutId);
    const layoutModelIds = (targetLayout?.models ?? [])
      .map((model) => model?.model_id ?? "")
      .filter((value): value is string => Boolean(value));
    const recordedCityModelIds = cityGlbModelIdsByLayout[selectedLayoutId] ?? [];
    const initialCandidates = recordedCityModelIds.length > 0 ? recordedCityModelIds : layoutModelIds;

    if (initialCandidates.length === 0) {
      setError(t.errorNoDownloadModel);
      return;
    }

    try {
      setStatus(t.statusDownloading);
      const checkedModelIds = new Set<string>();
      const freshCityEntries: Array<{ modelId: string; url: string }> = [];

      const triggerDownload = async (url: string, fileName: string) => {
        try {
          const response = await fetch(url);
          if (!response.ok) {
            throw new Error("download-failed");
          }
          const blob = await response.blob();
          const objectUrl = URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = objectUrl;
          link.download = fileName;
          document.body.appendChild(link);
          link.click();
          link.remove();
          window.setTimeout(() => URL.revokeObjectURL(objectUrl), 0);
          return;
        } catch {
          const link = document.createElement("a");
          link.href = url;
          link.target = "_blank";
          link.rel = "noopener noreferrer";
          link.download = fileName;
          document.body.appendChild(link);
          link.click();
          link.remove();
        }
      };

      const fetchFreshCityUrls = async (modelIds: string[]) => {
        for (const modelId of modelIds) {
          if (!modelId || checkedModelIds.has(modelId)) continue;
          checkedModelIds.add(modelId);

          // 下载时获取最新时效URL，避免使用缓存URL
          // eslint-disable-next-line no-await-in-loop
          const response = await getModelFile(modelId);
          const model = readModelFromResponse(response);
          const url = model?.presigned_url ?? "";
          if (isCityGlbUrl(url)) {
            freshCityEntries.push({ modelId, url });
          }
        }
      };

      await fetchFreshCityUrls(initialCandidates);

      if (freshCityEntries.length === 0 && recordedCityModelIds.length > 0) {
        const fallbackCandidates = layoutModelIds.filter((modelId) => !checkedModelIds.has(modelId));
        await fetchFreshCityUrls(fallbackCandidates);
      }

      if (freshCityEntries.length > 0 && selectedLayoutId) {
        dispatch(
          setLayoutCityGlbModelIds({
            layoutId: selectedLayoutId,
            modelIds: Array.from(new Set(freshCityEntries.map((entry) => entry.modelId))),
          })
        );
      }

      if (freshCityEntries.length === 0) {
        setStatus("");
        setError(t.errorNoDownloadModel);
        return;
      }

      for (const entry of freshCityEntries) {
        // eslint-disable-next-line no-await-in-loop
        await triggerDownload(entry.url, "city.glb");
      }

      setStatus(`${t.statusDownloadReady} (${freshCityEntries.length})`);
    } catch {
      setStatus("");
      setError(t.errorNoDownloadModel);
    }
  };

  return (
    <section className={workspaceShell}>
      <div className={workspaceBody}>
        <div className={workspaceMain}>
          <div className={workspaceColumns}>
            <div className={workspacePane}>
              <div className={`model-sidebar ${panelBase} flex h-full min-h-0 min-w-0 max-w-full flex-col gap-3`}>
                <div className="flex items-center justify-between gap-3 flex-shrink-0">
                  <h2 className="m-0 text-[16px]">{t.modelsTitle}</h2>
                  <div className={metaBase}>
                    <span>{t.total}: {layoutWithModels.length}</span>
                  </div>
                </div>
                {layoutWithModels.length === 0 ? (
                  <p className="text-[12px] text-[var(--muted)]">{t.empty}</p>
                ) : (
                  <div className={`${listBase} pretty-scrollbar overflow-y-auto overflow-x-hidden [scrollbar-gutter:stable_both-edges] flex-1 min-h-0 px-0`}>
                    {layoutWithModels.map((item, index) => (
                      <button
                        key={item.layout?.layout_id ?? `layout-${index}`}
                        type="button"
                        className={`${listItemBase} ${listItemInteractive} ${
                          selectedLayoutId === (item.layout?.layout_id ?? "") ? listItemSelected : ""
                        }`}
                        onClick={() => {
                          const lid = item.layout?.layout_id ?? "";
                          if (!lid) return;
                          void handleLayoutChange(lid);
                        }}
                      >
                        <div className="min-w-0 flex-1 text-left">
                          <div>Layout #{item.layout?.layout_id ?? "-"}</div>
                          <div className={`${listMeta} truncate`}>
                            {item.layout?.layout_name || "-"} · {t.modelCount}: {item.models?.length ?? 0}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className={`${workspacePane} flex flex-col gap-3`}>
              <div className={`model-toolbar ${panelBase} flex-shrink-0`}>
                <div className="flex flex-wrap items-center gap-3">
                  <h2 className="m-0 text-[16px]">{t.generateTitle}</h2>
                  <label className={fieldBase}>
                    <span>{t.layout_id}</span>
                    <input
                      className={inputBase}
                      value={layout_id}
                      onChange={(event) => setlayout_id(event.target.value)}
                    />
                  </label>
                  <label className={fieldBase}>
                    <span>{t.modelSelect}</span>
                    <select
                      className={inputBase}
                      value={selectedModelId}
                      onChange={(event) => {
                        void handleModelChange(event.target.value);
                      }}
                      disabled={selectedLayoutModels.length === 0}
                    >
                      <option value="">-</option>
                      {selectedLayoutModels.map((model, index) => {
                        const mid = model.model_id ?? "";
                        return (
                          <option key={mid || `model-option-${index}`} value={mid}>
                            {model.model_name || mid || "-"}
                          </option>
                        );
                      })}
                    </select>
                  </label>
                  <button className={`${buttonBase} ${buttonSmall}`} onClick={() => { void handleDownloadLayoutModels(); }}>
                    {t.downloadLayoutModels}
                  </button>
                </div>
                {status ? <p className={statusText}>{status}</p> : null}
                {error ? <p className={errorText}>{error}</p> : null}
              </div>

              <div className={`model-preview ${panelBase} flex-1 min-h-[clamp(360px,42vh,560px)] flex flex-col gap-3`}>
              
                <div className="flex-1 min-h-[clamp(280px,34vh,480px)]">
                  <ModelViewer objContents={objContents} glbUrls={glbUrls} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
