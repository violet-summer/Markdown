import { useState, useEffect } from "react";

type LayoutItem = {
  layout_id: string;
  svg_url: string;
  svg_content?: string;
  status: number;
  createdAt?: string;
  thumbnail?: string;
  layout_name?: string;
};

type LayoutListProps = {
  layouts: LayoutItem[];
  labels: {
    title: string;
    filterLabel: string;
    filterAll: string;
    filterDraft: string;
    filterRunning: string;
    filterDone: string;
    viewGrid: string;
    viewList: string;
    count: string;
    emptyTitle: string;
    emptyHint: string;
    statusDraft: string;
    statusRunning: string;
    statusDone: string;
    edit: string;
    generate: string;
    load: string;
    remove: string;
    createdAt: string;
    layoutPrefix: string;
    confirmDelete: (id: string) => string;
  };
  onEdit: (layout_id: string) => void;
  onGenerateModel: (layout_id: string) => void;
  onDelete: (layout_id: string) => void;
  onLoad: (layout_id: string) => void;
};

export function LayoutList({
  layouts,
  labels,
  onEdit,
  onGenerateModel,
  onDelete,
  onLoad,
}: LayoutListProps) {
  const buttonBase = "rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-2.5 py-1.5 text-[12px] font-semibold text-[var(--ink)] transition-all duration-150 hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-16px_var(--shadow)] disabled:cursor-not-allowed disabled:opacity-60";
  const buttonSmall = "px-3";
  const buttonPrimary = "border-transparent bg-[var(--accent)] text-[var(--button-foreground,var(--ink))]";
  const buttonSuccess = "border-transparent bg-[var(--accent-2)] text-[var(--button-foreground,var(--ink))]";
  const buttonDanger = "border-[#d3b2b2] text-[#8a2f2f]";
  const layoutShell = "grid h-full min-h-0 max-h-full grid-rows-[auto_minmax(0,1fr)] gap-4 overflow-hidden";
  const listHeader = "flex flex-wrap items-center justify-between gap-3";
  const listTitle = "m-0 text-[16px]";
  const listControls = "flex flex-wrap items-center gap-3 text-[12px] text-[var(--muted)]";
  const filterGroup = "flex items-center gap-2";
  const selectBase = "rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2 py-1.5 text-[12px] text-[var(--ink)]";
  const viewToggle = "flex flex-wrap gap-2";
  const countText = "text-[12px] text-[var(--muted)]";
  const emptyState = "rounded-[10px] border border-dashed border-[var(--border)] bg-[var(--surface-2)] px-4 py-6 text-center";
  const layoutGrid = "grid gap-4 sm:grid-cols-2 xl:grid-cols-3";
  const layoutList = "grid gap-3";
  const listContentShell = "h-full min-h-0 max-h-full overflow-y-auto overflow-x-hidden";
  const cardBase = "relative overflow-hidden rounded-[12px] border border-[var(--border)] bg-[var(--surface)] shadow-[0_12px_24px_-22px_var(--shadow)]";
  const cardSelected = "ring-2 ring-[var(--accent)]";
  const cardThumbnail = "relative aspect-[4/3] bg-[var(--surface-2)]";
  const thumbnailImage = "h-full w-full object-cover";
  const listItemBase = "flex items-center gap-4 rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3 transition-all hover:shadow-md";
  const listItemSelected = "ring-2 ring-[var(--accent)]";
  const listThumbnail = "relative h-16 w-16 shrink-0 overflow-hidden rounded-md bg-[var(--surface-2)]";
  const listInfo = "flex min-w-0 flex-1 flex-col gap-1";
  const listActions = "flex shrink-0 flex-wrap gap-2";
  const thumbnailPlaceholder = "grid h-full w-full place-items-center text-[11px] font-semibold text-[var(--muted)]";
  const statusBadgeBase = "absolute right-2 top-2 rounded-full border border-[var(--border)] bg-[var(--surface)] px-2 py-0.5 text-[10px] font-semibold text-[var(--muted)]";
  const statusBadgeRunning = "border-transparent bg-[var(--accent-2)] text-white";
  const statusBadgeDone = "border-transparent bg-[var(--accent)] text-white";
  const cardContent = "grid gap-2 px-4 py-3";
  const cardTitle = "m-0 text-[14px] font-semibold";
  const cardMeta = "text-[12px] text-[var(--muted)]";
  const cardActions = "flex flex-wrap gap-2";
  const [selectedLayout, setSelectedLayout] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"grid" | "list">("list");
  const [filterStatus, setFilterStatus] = useState<number | "all">("all");

  const resolveStatus = (status: unknown) => {
    const value = Number(status);
    return Number.isFinite(value) ? value : 0;
  };

  const filteredLayouts =
    filterStatus === "all"
      ? layouts
      : layouts.filter((l) => resolveStatus(l.status) === filterStatus);

  const handleEditClick = (layout_id: string) => {
    setSelectedLayout(layout_id);
    onEdit(layout_id);
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

  // SVG 缩略图缓存：layout_id -> { loading, error, svg }
  const [svgThumbs, setSvgThumbs] = useState<Record<string, { loading: boolean; error: boolean; svg: string }>>({});

  useEffect(() => {
    // 只为当前 filteredLayouts 拉取 SVG
    filteredLayouts.forEach((layout) => {
      if (svgThumbs[layout.layout_id] || !layout.layout_id) return;
      setSvgThumbs((prev) => ({ ...prev, [layout.layout_id]: { loading: true, error: false, svg: "" } }));
      fetch(`/api/layout/result/${layout.layout_id}`)
        .then(async (res) => {
          if (!res.ok) {
            const text = await res.text();
            console.error(`缩略图接口响应非200: layout_id=${layout.layout_id}, status=${res.status}, body=`, text);
            throw new Error(`接口响应非200: ${res.status}`);
          }
          return res.json();
        })
        .then((data) => {
          // 兼容 data.svg_content/data.svgContent
          const svg = data?.svg_content || data?.svgContent || "";
          if (!svg) {
            console.error(`SVG内容为空: layout_id=${layout.layout_id}, 返回数据=`, data);
          }
          setSvgThumbs((prev) => ({ ...prev, [layout.layout_id]: { loading: false, error: !svg, svg } }));
        })
        .catch((err) => {
          console.error(`拉取SVG缩略图失败: layout_id=${layout.layout_id}`, err);
          setSvgThumbs((prev) => ({ ...prev, [layout.layout_id]: { loading: false, error: true, svg: "" } }));
        });
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filteredLayouts]);

  return (
    <div className={layoutShell}>
      <div className={listHeader}>
        {labels.title ? <h2 className={listTitle}>{labels.title}</h2> : null}
        <div className={listControls}>
          <div className={filterGroup}>
            <label>{labels.filterLabel}</label>
            <select
              className={selectBase}
              value={filterStatus}
              onChange={(e) =>
                setFilterStatus(e.target.value === "all" ? "all" : Number(e.target.value))
              }
            >
              <option value="all">{labels.filterAll}</option>
              <option value="0">{labels.filterDraft}</option>
              <option value="1">{labels.filterRunning}</option>
              <option value="2">{labels.filterDone}</option>
            </select>
          </div>
          <div className={viewToggle}>
            <button
              className={`${buttonBase} ${buttonSmall} ${viewMode === "grid" ? buttonPrimary : ""}`}
              onClick={() => setViewMode("grid")}
            >
              {labels.viewGrid}
            </button>
            <button
              className={`${buttonBase} ${buttonSmall} ${viewMode === "list" ? buttonPrimary : ""}`}
              onClick={() => setViewMode("list")}
            >
              {labels.viewList}
            </button>
          </div>
          <span className={countText}>{labels.count} {filteredLayouts.length}</span>
        </div>
      </div>

      <div className={listContentShell}>
      {filteredLayouts.length === 0 ? (
        <div className={emptyState}>
          <p>{labels.emptyTitle}</p>
          <p className="text-[12px] text-[var(--muted)]">{labels.emptyHint}</p>
        </div>
      ) : (
        <div className={viewMode === "grid" ? layoutGrid : layoutList}>
          {filteredLayouts.map((layout) => {
            const thumb = svgThumbs[layout.layout_id];
            const layoutStatus = resolveStatus(layout.status);
            const canGenerateModel = layoutStatus === 0 || layoutStatus === 2;
            
            if (viewMode === "list") {
              return (
                <div
                  key={layout.layout_id}
                  className={`${listItemBase} ${selectedLayout === layout.layout_id ? listItemSelected : ""}`}
                >
                  <div className={listThumbnail}>
                    {thumb && !thumb.loading && !thumb.error && thumb.svg ? (
                      <svg
                        style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                        dangerouslySetInnerHTML={{ __html: thumb.svg.replace(/<svg[\s\S]*?>|<\/svg>/g, '') }}
                        viewBox={(() => {
                          const match = thumb.svg.match(/viewBox="([^"]+)"/);
                          if (match) return match[1];
                          const w = thumb.svg.match(/width="(\d+(?:\.\d+)?)"/);
                          const h = thumb.svg.match(/height="(\d+(?:\.\d+)?)"/);
                          if (w && h) return `0 0 ${w[1]} ${h[1]}`;
                          return undefined;
                        })()}
                        xmlns="http://www.w3.org/2000/svg"
                        preserveAspectRatio="xMidYMid slice"
                      />
                    ) : thumb && thumb.loading ? (
                      <div className="grid h-full w-full place-items-center text-[10px] text-[var(--muted)]">...</div>
                    ) : (
                      <div className="grid h-full w-full place-items-center text-[10px] text-[var(--muted)]">SVG</div>
                    )}
                  </div>
                  
                  <div className={listInfo}>
                    <div className="flex items-center gap-2">
                      <h3 className="m-0 truncate text-[14px] font-semibold">
                        {layout.layout_name
                          ? `${labels.layoutPrefix} ${layout.layout_name}`
                          : `${labels.layoutPrefix} ${layout.layout_id}`}
                      </h3>
                      <span
                        className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                          layoutStatus === 2
                            ? "bg-[var(--accent)] text-white"
                            : layoutStatus === 1
                            ? "bg-[var(--accent-2)] text-white"
                            : "border border-[var(--border)] bg-[var(--surface)] text-[var(--muted)]"
                        }`}
                      >
                        {layoutStatus === 0 && labels.statusDraft}
                        {layoutStatus === 1 && labels.statusRunning}
                        {layoutStatus === 2 && labels.statusDone}
                      </span>
                    </div>
                    {layout.createdAt && (
                      <p className="m-0 truncate text-[12px] text-[var(--muted)]">
                        {labels.createdAt}: {layout.createdAt}
                      </p>
                    )}
                  </div>
                  
                  <div className={listActions}>
                    <button
                      className={`${buttonBase} ${buttonSmall} `}
                      onClick={() => handleEditClick(layout.layout_id)}
                      title="可视化编辑SVG"
                    >
                      ✏️ {labels.edit}
                    </button>
                    <button
                      className={`${buttonBase} ${buttonSmall} `}
                      onClick={() => onGenerateModel(layout.layout_id)}
                      title="生成3D模型"
                      disabled={!canGenerateModel}
                    >
                      🏗️ {labels.generate}
                    </button>
                    <button
                      className={`${buttonBase} ${buttonSmall}`}
                      onClick={() => onLoad(layout.layout_id)}
                      title="加载到编辑器"
                    >
                      📥 {labels.load}
                    </button>
                    <button
                      className={`${buttonBase} ${buttonSmall} ${buttonDanger}`}
                      onClick={() => {
                        if (confirm(labels.confirmDelete(layout.layout_id))) {
                          onDelete(layout.layout_id);
                        }
                      }}
                      title="删除布局"
                    >
                      🗑️ {labels.remove}
                    </button>
                  </div>
                </div>
              );
            }
            
            return (
              <div
                key={layout.layout_id}
                className={`${cardBase} ${selectedLayout === layout.layout_id ? cardSelected : ""}`}
              >
                <div className={cardThumbnail}>
                  {thumb && !thumb.loading && !thumb.error && thumb.svg ? (
                    <div
                      className={thumbnailImage + " flex items-center justify-center bg-white"}
                      style={{ minHeight: 0, minWidth: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fff', padding: 0 }}
                    >
                      {/* 缩略图铺满卡片，长边裁切，视觉密度统一 */}
                      <svg
                        style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                        dangerouslySetInnerHTML={{ __html: thumb.svg.replace(/<svg[\s\S]*?>|<\/svg>/g, '') }}
                        viewBox={(() => {
                          const match = thumb.svg.match(/viewBox="([^"]+)"/);
                          if (match) return match[1];
                          const w = thumb.svg.match(/width="(\d+(?:\.\d+)?)"/);
                          const h = thumb.svg.match(/height="(\d+(?:\.\d+)?)"/);
                          if (w && h) return `0 0 ${w[1]} ${h[1]}`;
                          return undefined;
                        })()}
                        xmlns="http://www.w3.org/2000/svg"
                        preserveAspectRatio="xMidYMid slice"
                      />
                    </div>
                  ) : thumb && thumb.loading ? (
                    <div className={thumbnailPlaceholder}>加载中...</div>
                  ) : thumb && thumb.error ? (
                    <div className={thumbnailPlaceholder}>加载失败</div>
                  ) : (
                    <div className={thumbnailPlaceholder}><span>SVG</span></div>
                  )}
                  <div
                    className={`${statusBadgeBase} ${
                      layoutStatus === 2 ? statusBadgeDone : layoutStatus === 1 ? statusBadgeRunning : ""
                    }`}
                  >
                    {layoutStatus === 0 && labels.statusDraft}
                    {layoutStatus === 1 && labels.statusRunning}
                    {layoutStatus === 2 && labels.statusDone}
                  </div>
                </div>

                <div className={cardContent}>
                  <h3 className={cardTitle}>
                    {layout.layout_name
                      ? `${labels.layoutPrefix} ${layout.layout_name}`
                      : `${labels.layoutPrefix} ${layout.layout_id}`}
                  </h3>
                  {layout.createdAt && (
                    <p className={cardMeta}>{labels.createdAt}: {layout.createdAt}</p>
                  )}

                  <div className={cardActions}>
                    <button
                      className={`${buttonBase} ${buttonSmall} ${buttonPrimary}`}
                      onClick={() => handleEditClick(layout.layout_id)}
                      title="可视化编辑SVG"
                    >
                      ✏️ {labels.edit}
                    </button>
                    <button
                      className={`${buttonBase} ${buttonSmall} ${buttonSuccess}`}
                      onClick={() => onGenerateModel(layout.layout_id)}
                      title="生成3D模型"
                      disabled={!canGenerateModel}
                    >
                      🏗️ {labels.generate}
                    </button>
                    <button
                      className={`${buttonBase} ${buttonSmall}`}
                      onClick={() => onLoad(layout.layout_id)}
                      title="加载到编辑器"
                    >
                      📥 {labels.load}
                    </button>
                    <button
                      className={`${buttonBase} ${buttonSmall} ${buttonDanger}`}
                      onClick={() => {
                        if (confirm(labels.confirmDelete(layout.layout_id))) {
                          onDelete(layout.layout_id);
                        }
                      }}
                      title="删除布局"
                    >
                      🗑️ {labels.remove}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
      </div>
    </div>
  );
}
