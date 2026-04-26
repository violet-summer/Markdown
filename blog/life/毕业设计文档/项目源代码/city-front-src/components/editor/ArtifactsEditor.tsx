import { useEffect, useMemo, useState, useRef } from "react";

type Point = { x: number; y: number };

type ArtifactsEditorProps = {
  mode: "streamlines" | "polygons";
  data: Record<string, any> | null;
  showOverview?: boolean;
  labels?: {
    layer: string;
    feature: string;
    grid: string;
    zoom: string;
    undo?: string;
    deletePoint: string;
    showLayers: string;
    hideLayers: string;
    hint: string;
  };
  onChange: (next: Record<string, any>) => void;
  // 父组件传入的额外控件
  onSaveArtifacts?: () => void;
  onModeChange?: (mode: "streamlines" | "polygons") => void;
  layoutSelector?: React.ReactNode;
  saveArtifactsLabel?: string;
  streamlinesLabel?: string;
  polygonsLabel?: string;
};

type LayerConfig = {
  key: string;
  label: string;
  kind: "polygon";
  get: (data: Record<string, any>) => Point[][];
  set: (data: Record<string, any>, features: Point[][]) => void;
};

const NON_EDITABLE_KEYS = new Set([
  "origin",
  "worldDimensions",
  "secondaryRoadPolygon",
  "smallParksPolygons",
]);

const isPoint = (value: unknown): value is Point => {
  if (!value || typeof value !== "object") {
    return false;
  }
  const candidate = value as Record<string, unknown>;
  return Number.isFinite(Number(candidate.x)) && Number.isFinite(Number(candidate.y));
};

const normalizePointPath = (value: unknown): Point[] => {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .filter((item) => isPoint(item))
    .map((item) => ({ x: Number(item.x), y: Number(item.y) }));
};

const extractFeatures = (value: unknown): Point[][] => {
  if (!Array.isArray(value) || value.length === 0) {
    return [];
  }

  if (Array.isArray(value[0])) {
    return value
      .map((item) => normalizePointPath(item))
      .filter((item) => item.length > 0);
  }

  if (isPoint(value[0])) {
    const singlePath = normalizePointPath(value);
    return singlePath.length > 0 ? [singlePath] : [];
  }

  return [];
};

const writeFeatures = (original: unknown, features: Point[][]) => {
  if (!Array.isArray(original) || original.length === 0) {
    return features;
  }

  if (Array.isArray(original[0])) {
    return features;
  }

  if (isPoint(original[0])) {
    return features[0] ?? [];
  }

  return features;
};

const LAYER_LABELS_ZH: Record<string, string> = {
  bigParksPolygon: "大型公园",
  blocksPolygon: "街区",
  coastlinePolygon: "海岸线",
  dividedBuildingsPolygons: "建筑分割区",
  groundPolygon: "地面边界",
  mainExteriorInteriorRoadPolygon: "主路内外环",
  mainNormalRoadPolygon: "主路",
  majorExteriorInteriorRoadPolygon: "次主路内外环",
  majorNormalRoadPolygon: "次主路",
  minorExteriorInteriorRoadPolygon: "支路内外环",
  minorNormalRoadPolygon: "支路",
  polygonsToProcess: "待处理多边形",
  riverPolygon: "河道",
  seaPolygon: "海域",
  waterRoadPolygon: "水路",
  waterSecondaryRoadPolygon: "次级水路",
};

const toLayerLabel = (key: string) => LAYER_LABELS_ZH[key] ?? key.replace(/([a-z])([A-Z])/g, "$1 $2");

const isExteriorInteriorLayer = (key: string) =>
  key === "mainExteriorInteriorRoadPolygon" ||
  key === "majorExteriorInteriorRoadPolygon" ||
  key === "minorExteriorInteriorRoadPolygon";

const isInteriorRingFeature = (layerKey: string, featureIndex: number) =>
  isExteriorInteriorLayer(layerKey) && featureIndex % 2 === 1;

const getRingPairStartIndex = (featureIndex: number) => (featureIndex % 2 === 0 ? featureIndex : featureIndex - 1);

const cloneData = (value: Record<string, any> | null) => {
  if (typeof structuredClone === "function") {
    return structuredClone(value ?? {});
  }
  return JSON.parse(JSON.stringify(value ?? {}));
};

const distanceSq = (a: Point, b: Point) => {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return dx * dx + dy * dy;
};

const distanceToSegmentSq = (p: Point, a: Point, b: Point) => {
  const abx = b.x - a.x;
  const aby = b.y - a.y;
  const apx = p.x - a.x;
  const apy = p.y - a.y;
  const abLenSq = abx * abx + aby * aby;
  if (abLenSq === 0) return distanceSq(p, a);
  const t = Math.max(0, Math.min(1, (apx * abx + apy * aby) / abLenSq));
  const proj = { x: a.x + abx * t, y: a.y + aby * t };
  return distanceSq(p, proj);
};

const insertPoint = (points: Point[], nextPoint: Point, isPolygon: boolean) => {
  if (points.length < 2) {
    return [...points, nextPoint];
  }
  let bestIndex = 1;
  let bestDist = Number.POSITIVE_INFINITY;
  const lastIndex = points.length - 1;
  const segmentCount = isPolygon ? points.length : points.length - 1;
  for (let index = 0; index < segmentCount; index += 1) {
    const start = points[index];
    const end = points[(index + 1) % points.length];
    const dist = distanceToSegmentSq(nextPoint, start, end);
    if (dist < bestDist) {
      bestDist = dist;
      bestIndex = index + 1;
    }
  }
  const next = points.slice();
  next.splice(bestIndex, 0, nextPoint);
  return next;
};

export function ArtifactsEditor({
  mode,
  data,
  showOverview = false,
  labels,
  onChange,
  onSaveArtifacts,
  onModeChange,
  layoutSelector,
  saveArtifactsLabel,
  streamlinesLabel,
  polygonsLabel,
}: ArtifactsEditorProps) {
  const ui = labels ?? {
    layer: "图层",
    feature: "要素",
    grid: "网格",
    zoom: "缩放",
    undo: "撤回",
    deletePoint: "删除点",
    showLayers: "显示图层",
    hideLayers: "隐藏图层",
  };

  const layers = useMemo<LayerConfig[]>(() => {
    const source = data ?? {};
    return Object.keys(source)
      .filter((key) => !NON_EDITABLE_KEYS.has(key))
      .filter((key) => extractFeatures(source[key]).length > 0)
      .map((key) => ({
        key,
        label: toLayerLabel(key),
        kind: "polygon",
        get: (payload) => extractFeatures(payload?.[key]),
        set: (payload, features) => {
          payload[key] = writeFeatures(payload?.[key], features);
        },
      }));
  }, [data]);

  const [activeLayerKey, setActiveLayerKey] = useState(layers[0]?.key ?? "");
  const [selectedFeatureIndex, setSelectedFeatureIndex] = useState(0);
  const [selectedPointIndex, setSelectedPointIndex] = useState<number | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [gridSize, setGridSize] = useState(1);
  const [zoom, setZoom] = useState(1);
  const [containerSize, setContainerSize] = useState({ width: 1200, height: 800 });
  const containerRef = useRef<HTMLDivElement>(null);

  const [layerVisibility, setLayerVisibility] = useState<Record<string, boolean>>({});
  const [showOverlayPanel, setShowOverlayPanel] = useState(false);
  const [canUndo, setCanUndo] = useState(false);
  const undoStackRef = useRef<Record<string, any>[]>([]);
  const dragSnapshotTakenRef = useRef(false);

  const activeLayer = layers.find((layer) => layer.key === activeLayerKey) ?? layers[0];
  const features = activeLayer && data ? activeLayer.get(data) : [];
  const feature = features[selectedFeatureIndex] ?? [];

  useEffect(() => {
    setLayerVisibility((current) => {
      const next: Record<string, boolean> = {};
      layers.forEach((layer) => {
        next[layer.key] = typeof current[layer.key] === "boolean" ? current[layer.key] : true;
      });
      return next;
    });
  }, [layers]);

  useEffect(() => {
    if (!layers.some((layer) => layer.key === activeLayerKey)) {
      setActiveLayerKey(layers[0]?.key ?? "");
    }
  }, [layers, activeLayerKey]);

  useEffect(() => {
    setSelectedFeatureIndex(0);
    setSelectedPointIndex(null);
  }, [activeLayerKey, mode]);

  const worldDimensions = data?.worldDimensions ?? data?.world_dimensions ?? { x: 100, y: 100 };
  const origin = data?.origin ?? { x: 0, y: 0 };

  // 监听容器尺寸变化
  useEffect(() => {
    if (!containerRef.current) return;
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        if (width > 0 && height > 0) {
          setContainerSize({ width: Math.floor(width - 32), height: Math.floor(height - 32) });
        }
      }
    });
    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  const { scale, canvasWidth, canvasHeight } = useMemo(() => {
    const maxWidth = containerSize.width;
    const maxHeight = containerSize.height;
    const worldWidth = Math.max(worldDimensions.x, 1);
    const worldHeight = Math.max(worldDimensions.y, 1);
    const scaleFactor = Math.min(maxWidth / worldWidth, maxHeight / worldHeight) * zoom;
    return {
      scale: scaleFactor,
      canvasWidth: Math.max(200, worldWidth * scaleFactor),
      canvasHeight: Math.max(200, worldHeight * scaleFactor),
    };
  }, [worldDimensions.x, worldDimensions.y, zoom, containerSize]);

  const toCanvas = (point: Point) => ({
    x: (point.x - origin.x) * scale,
    y: (point.y - origin.y) * scale,
  });

  const toWorld = (point: Point) => ({
    x: point.x / scale + origin.x,
    y: point.y / scale + origin.y,
  });

  const snapPoint = (point: Point) => {
    if (!gridSize || gridSize <= 0) return point;
    return {
      x: Math.round(point.x / gridSize) * gridSize,
      y: Math.round(point.y / gridSize) * gridSize,
    };
  };

  const updateFeature = (nextFeature: Point[]) => {
    if (!activeLayer || !data) return;
    const nextFeatures = features.slice();
    nextFeatures[selectedFeatureIndex] = nextFeature;
    const nextData = cloneData(data);
    activeLayer.set(nextData, nextFeatures);
    onChange(nextData);
  };

  const pushUndoSnapshot = () => {
    if (!data) return;
    undoStackRef.current.push(cloneData(data));
    if (undoStackRef.current.length > 100) {
      undoStackRef.current.shift();
    }
    setCanUndo(undoStackRef.current.length > 0);
  };

  const handleUndo = () => {
    const previous = undoStackRef.current.pop();
    if (!previous) return;
    onChange(cloneData(previous));
    setSelectedPointIndex(null);
    setCanUndo(undoStackRef.current.length > 0);
  };

  const handleDeletePoint = () => {
    if (selectedPointIndex === null) return;
    const minPoints = activeLayer?.kind === "polygon" ? 3 : 0;
    if (feature.length <= minPoints) return;
    pushUndoSnapshot();
    const next = feature.filter((_, index) => index !== selectedPointIndex);
    updateFeature(next);
    setSelectedPointIndex(null);
  };

  const renderCanvas = (canvas: HTMLCanvasElement | null) => {
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    ctx.fillStyle = "rgba(255,255,255,0)";
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);

    ctx.strokeStyle = "#e0e0e0";
    ctx.lineWidth = 0.5;
    const grid = Math.max(gridSize * scale, 10);
    for (let x = 0; x < canvasWidth; x += grid) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvasHeight);
      ctx.stroke();
    }
    for (let y = 0; y < canvasHeight; y += grid) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvasWidth, y);
      ctx.stroke();
    }

    const drawFeature = (
      points: Point[],
      kind: "polyline" | "polygon",
      stroke: string,
      fill: string,
      lineWidth: number,
    ) => {
      if (points.length < 2) return;
      ctx.strokeStyle = stroke;
      ctx.lineWidth = lineWidth;
      ctx.beginPath();
      const first = toCanvas(points[0]);
      ctx.moveTo(first.x, first.y);
      for (let index = 1; index < points.length; index += 1) {
        const next = toCanvas(points[index]);
        ctx.lineTo(next.x, next.y);
      }
      if (kind === "polygon") {
        ctx.closePath();
        ctx.fillStyle = fill;
        ctx.fill();
      }
      ctx.stroke();
    };

    const tracePolygon = (points: Point[]) => {
      if (points.length < 2) return;
      const first = toCanvas(points[0]);
      ctx.moveTo(first.x, first.y);
      for (let index = 1; index < points.length; index += 1) {
        const next = toCanvas(points[index]);
        ctx.lineTo(next.x, next.y);
      }
      ctx.closePath();
    };

    const drawRingBetween = (
      exterior: Point[],
      interior: Point[],
      stroke: string,
      fill: string,
      lineWidth: number,
      interiorStroke = stroke,
    ) => {
      if (exterior.length < 2) return;

      ctx.beginPath();
      tracePolygon(exterior);
      if (interior.length >= 2) {
        tracePolygon(interior);
      }
      ctx.fillStyle = fill;
      ctx.fill("evenodd");

      ctx.strokeStyle = stroke;
      ctx.lineWidth = lineWidth;
      ctx.beginPath();
      tracePolygon(exterior);
      ctx.stroke();

      if (interior.length >= 2) {
        ctx.strokeStyle = interiorStroke;
        ctx.lineWidth = lineWidth;
        ctx.beginPath();
        tracePolygon(interior);
        ctx.stroke();
      }
    };

    if (data) {
      layers.forEach((layer) => {
        if (!layerVisibility[layer.key]) {
          return;
        }
        const layerFeatures = layer.get(data);
        layerFeatures.forEach((points, featureIndex) => {
          if (isExteriorInteriorLayer(layer.key)) {
            if (isInteriorRingFeature(layer.key, featureIndex)) {
              return;
            }
            const interior = layerFeatures[featureIndex + 1] ?? [];
            drawRingBetween(
              points,
              interior,
              "rgba(71,85,105,0.75)",
              "rgba(148,163,184,0.16)",
              1.2,
              "rgba(51,65,85,0.75)",
            );
            return;
          }

          drawFeature(points, "polygon", "rgba(71,85,105,0.7)", "rgba(148,163,184,0.1)", 1.2);
        });
      });
    }

    if (activeLayer && isExteriorInteriorLayer(activeLayer.key)) {
      const pairStartIndex = getRingPairStartIndex(selectedFeatureIndex);
      const exterior = features[pairStartIndex] ?? [];
      const interior = features[pairStartIndex + 1] ?? [];
      drawRingBetween(exterior, interior, "#f97316", "rgba(249,115,22,0.2)", 2.4, "#0f766e");
    } else {
      drawFeature(feature, activeLayer?.kind ?? "polyline", "#f97316", "rgba(249,115,22,0.2)", 2.4);
    }

    feature.forEach((point, index) => {
      const canvasPoint = toCanvas(point);
      ctx.fillStyle = index === selectedPointIndex ? "#f97316" : "#ffffff";
      ctx.strokeStyle = "#f97316";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(canvasPoint.x, canvasPoint.y, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    });
  };

  const [canvasRef, setCanvasRef] = useState<HTMLCanvasElement | null>(null);

  useEffect(() => {
    renderCanvas(canvasRef);
  }, [canvasRef, feature, selectedPointIndex, gridSize, canvasWidth, canvasHeight, activeLayer?.kind, scale, layers, layerVisibility, data]);

  const findPointIndex = (worldPoint: Point) => {
    let closestIndex: number | null = null;
    let closestDistance = Number.POSITIVE_INFINITY;
    feature.forEach((point, index) => {
      const dist = distanceSq(point, worldPoint);
      if (dist < closestDistance) {
        closestDistance = dist;
        closestIndex = index;
      }
    });
    if (closestIndex === null) return null;
    const threshold = (6 / scale) * (6 / scale);
    return closestDistance <= threshold ? closestIndex : null;
  };

  const handlePointerDown = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!activeLayer) return;
    const rect = event.currentTarget.getBoundingClientRect();
    const worldPoint = toWorld({ x: event.clientX - rect.left, y: event.clientY - rect.top });
    const snapped = snapPoint(worldPoint);

    const pointIndex = findPointIndex(snapped);
    if (pointIndex !== null) {
      setSelectedPointIndex(pointIndex);
      dragSnapshotTakenRef.current = false;
      setIsDragging(true);
      return;
    }

    pushUndoSnapshot();
    const updated = insertPoint(feature, snapped, activeLayer.kind === "polygon");
    updateFeature(updated);
    setSelectedPointIndex(updated.length - 1);
  };

  const handlePointerMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDragging || selectedPointIndex === null) return;
    const rect = event.currentTarget.getBoundingClientRect();
    const worldPoint = toWorld({ x: event.clientX - rect.left, y: event.clientY - rect.top });
    const snapped = snapPoint(worldPoint);
    const currentPoint = feature[selectedPointIndex];
    if (!currentPoint) return;
    if (currentPoint.x === snapped.x && currentPoint.y === snapped.y) {
      return;
    }
    if (!dragSnapshotTakenRef.current) {
      pushUndoSnapshot();
      dragSnapshotTakenRef.current = true;
    }
    const next = feature.map((point, index) => (index === selectedPointIndex ? snapped : point));
    updateFeature(next);
  };

  const handlePointerUp = () => {
    setIsDragging(false);
    dragSnapshotTakenRef.current = false;
  };

  const buttonBase = "rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-2.5 py-1.5 text-[12px] font-semibold transition-colors duration-150 hover:brightness-95 active:brightness-90 focus:outline-none disabled:cursor-not-allowed disabled:opacity-60";
  const buttonPrimary = "border-[var(--accent)] bg-[var(--accent)] text-[var(--button-foreground,var(--ink))] hover:brightness-95 active:brightness-90";
  const buttonGhost = "bg-transparent text-[var(--ink)]";
  const buttonSmall = "px-3";
  const fieldBase = "flex items-center gap-2 flex-shrink-0";
  const labelText = "text-[11px] text-[var(--muted)] whitespace-nowrap font-medium";
  const inputBase = "rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2.5 py-2 text-[13px] text-[var(--ink)]";
  const inputCompact = "rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2 py-1 text-[12px] text-[var(--ink)] w-20 focus:outline-none focus:ring-2 focus:ring-[var(--accent)] focus:border-transparent transition-all";
  const selectCompact = "rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2 py-1 text-[12px] text-[var(--ink)] min-w-[100px] max-w-[140px] focus:outline-none focus:ring-2 focus:ring-[var(--accent)] focus:border-transparent transition-all cursor-pointer";
  const buttonRowBase = "flex flex-wrap gap-3 mt-2";
  const editorShell = "grid gap-3 grid-rows-[auto_1fr] h-full";
  const toolbarShell = "flex flex-nowrap items-center gap-2.5 overflow-x-auto pb-2 text-[12px] border-b border-[var(--border)]";
  const toolbarDivider = "h-6 w-px bg-[var(--border)] flex-shrink-0";
  const canvasShell = "relative overflow-hidden rounded-[12px] border border-[var(--border)] bg-[var(--surface)] shadow-[0_6px_12px_-10px_var(--shadow)] flex items-center justify-center w-full h-full";
  const hintText = "text-[12px] text-[var(--muted)]";

  return (
    <div className={editorShell}>
      <div className={toolbarShell}>
        {layoutSelector && <div className="flex-shrink-0">{layoutSelector}</div>}
        {onSaveArtifacts && (
          <button
            className={`${buttonBase}  flex-shrink-0`}
            type="button"
            onClick={onSaveArtifacts}
          >
            {saveArtifactsLabel || "保存要素"}
          </button>
        )}
        {(layoutSelector || onSaveArtifacts) && (
          <div className={toolbarDivider}></div>
        )}
        <label className={fieldBase}>
          <span className={labelText}>{ui.layer}</span>
          <select
            className={selectCompact}
            value={activeLayerKey}
            onChange={(event) => setActiveLayerKey(event.target.value)}
          >
            {layers.map((layer) => (
              <option key={layer.key} value={layer.key}>
                {layer.label}
              </option>
            ))}
          </select>
        </label>
        <label className={fieldBase}>
          <span className={labelText}>{ui.feature}</span>
          <select
            className={selectCompact}
            value={selectedFeatureIndex}
            onChange={(event) => setSelectedFeatureIndex(Number(event.target.value))}
          >
            {features.map((_, index) => (
              <option key={`${activeLayerKey}-${index}`} value={index}>
                {activeLayer?.label} #{index + 1}
              </option>
            ))}
          </select>
        </label>
        <label className={fieldBase}>
          <span className={labelText}>{ui.grid}</span>
          <input
            className={inputCompact}
            type="number"
            min="0"
            step="0.5"
            value={gridSize}
            onChange={(event) => setGridSize(Number(event.target.value))}
          />
        </label>
        <label className={fieldBase}>
          <span className={labelText}>{ui.zoom}</span>
          <button
            className={`${buttonBase} ${buttonSmall} flex-shrink-0 w-8 px-0`}
            type="button"
            onClick={() => setZoom((z) => Math.max(0.5, Number((z - 0.1).toFixed(2))))}
            title="缩小"
          >
            -
          </button>
          <button
            className="text-[11px] font-medium text-[var(--ink)] whitespace-nowrap min-w-[44px] text-center hover:text-[var(--accent)] cursor-pointer transition-colors rounded px-1 hover:bg-[var(--surface-2)]"
            type="button"
            onClick={() => setZoom(1)}
            title="点击重置为100%"
          >
            {Math.round(zoom * 100)}%
          </button>
          <button
            className={`${buttonBase} ${buttonSmall} flex-shrink-0 w-8 px-0`}
            type="button"
            onClick={() => setZoom((z) => Math.min(2, Number((z + 0.1).toFixed(2))))}
            title="放大"
          >
            +
          </button>
        </label>
        <div className={toolbarDivider}></div>
        <button
          className={`${buttonBase} ${buttonSmall} flex-shrink-0`}
          type="button"
          onClick={handleUndo}
          disabled={!canUndo}
        >
          {ui.undo || "撤回"}
        </button>
        <button
          className={`${buttonBase} ${buttonSmall} flex-shrink-0`}
          type="button"
          onClick={handleDeletePoint}
          disabled={selectedPointIndex === null}
        >
          {ui.deletePoint}
        </button>
        <button
          className={`${buttonBase} ${buttonSmall} flex-shrink-0`}
          type="button"
          onClick={() => setShowOverlayPanel(!showOverlayPanel)}
        >
          {showOverlayPanel ? ui.hideLayers : ui.showLayers}
        </button>
      </div>

      {showOverlayPanel && (
        <div className="mt-3 grid gap-2 rounded-[10px] border border-[var(--border)] bg-[var(--surface-2)] p-3 text-[12px]">
          <div className="text-[12px] font-semibold text-[var(--muted)]">叠加图层</div>
          {layers.map((layer) => (
            <div key={layer.key} className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2">
              <label className="flex items-center gap-2 text-[12px] text-[var(--ink)]">
                <input
                  type="checkbox"
                  checked={Boolean(layerVisibility[layer.key])}
                  onChange={(e) => {
                    setLayerVisibility((current) => ({
                      ...current,
                      [layer.key]: e.target.checked,
                    }));
                  }}
                />
                <span className="truncate">{layer.label}</span>
              </label>
              <span className="text-[11px] text-[var(--muted)]">{layer.get(data ?? {}).length}</span>
            </div>
          ))}
        </div>
      )}

      <div ref={containerRef} className={canvasShell}>
        <canvas
          ref={setCanvasRef}
          width={canvasWidth}
          height={canvasHeight}
          onMouseDown={handlePointerDown}
          onMouseMove={handlePointerMove}
          onMouseUp={handlePointerUp}
          onMouseLeave={handlePointerUp}
        />
      </div>

      {/* <div className={hintText}>
        {ui.hint}
      </div> */}
    </div>
  );
}
