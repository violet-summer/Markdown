import { useState, useEffect, useRef } from "react";
import type { PointerEvent as ReactPointerEvent } from "react";
import { saveLayoutEdit, generate3DModel, getLayoutProgress } from "@/api/layout";

type Layer = {
  id: string;
  name: string;
  visible: boolean;
  color?: string;
};

type SvgVisualEditorProps = {
  svgUrl: string;          // SVG文件URL（后端生成的）
  layout_id: number;        // 布局ID
  width?: number;
  height?: number;
};

/**
 * SVG可视化编辑器
 * 
 * 功能：
 * 1. 加载并显示后端生成的SVG（layout.svg）
 * 2. 提供图层控制（显示/隐藏）
 * 3. 编辑功能（未来扩展：点击编辑、拖拽调整）
 * 4. 保存编辑到服务器（更新JSON和SVG）
 * 5. 触发3D模型生成（使用编辑后的数据）
 */
export function SvgVisualEditor({
  svgUrl,
  layout_id,
  width = 800,
  height = 600,
}: SvgVisualEditorProps) {
  const buttonBase = "rounded-[10px] border border-[var(--border)] bg-[var(--surface)] px-2.5 py-1.5 text-[12px] font-semibold transition-all duration-150 hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-16px_var(--shadow)] disabled:cursor-not-allowed disabled:opacity-60";
  const buttonSmall = "px-3";
  const buttonPrimary = "border-transparent bg-[var(--accent)] text-white";
  const buttonDanger = "border-[#d3b2b2] text-[#8a2f2f]";
  // 图层管理
  const [layers, setLayers] = useState<Layer[]>([]);
  const [layerVisibility, setLayerVisibility] = useState<Record<string, boolean>>({});
  
  // SVG内容（用于提取图层信息）
  const [svg_content, setsvg_content] = useState<string>("");
  
  // 3D生成状态
  const [isGenerating3D, setIsGenerating3D] = useState(false);
  const [generation3DProgress, setGeneration3DProgress] = useState(0);
  const [generation3DStatus, setGeneration3DStatus] = useState("");
  
  // 编辑状态
  const [isEditing, setIsEditing] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  
  // 缩放
  const [zoom, setZoom] = useState(100);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const isPanningRef = useRef(false);
  const panStartRef = useRef({ x: 0, y: 0, panX: 0, panY: 0 });

  /**
   * 加载SVG内容并提取图层信息
   */
  useEffect(() => {
    const fetchSvg = async () => {
      try {
        const response = await fetch(svgUrl);
        const text = await response.text();
        setsvg_content(text);
        
        // 解析SVG提取图层
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, "image/svg+xml");
        const svgElement = doc.querySelector("svg");
        
        if (svgElement) {
          const parsedLayers: Layer[] = [];
          const visibility: Record<string, boolean> = {};
          
          // 提取所有<g>标签作为图层
          Array.from(svgElement.getElementsByTagName("g")).forEach((gElement, index) => {
            const layerId = gElement.getAttribute("id") || `layer-${index}`;
            const className = gElement.getAttribute("class") || "";
            
            // 从class名称提取友好的图层名
            let layerName = className
              .replace(/^layer-/, "")
              .replace(/-/g, " ")
              .toUpperCase();
            
            if (layerName === "") {
              layerName = `图层 ${index + 1}`;
            }
            
            parsedLayers.push({
              id: layerId,
              name: layerName,
              visible: true,
            });
            
            visibility[layerId] = true;
          });
          
          setLayers(parsedLayers);
          setLayerVisibility(visibility);
        }
      } catch (error) {
        console.error("加载SVG失败:", error);
      }
    };
    
    if (svgUrl) {
      fetchSvg();
    }
  }, [svgUrl]);

  /**
   * 切换图层可见性
   */
  const toggleLayerVisibility = (layerId: string) => {
    setLayerVisibility(prev => ({
      ...prev,
      [layerId]: !prev[layerId]
    }));
    setHasChanges(true);
  };

  /**
   * 保存编辑到服务器
   * 更新JSON和SVG文件
   */
  const handleSaveEdit = async () => {
    if (!hasChanges) return;
    
    try {
      const result = await saveLayoutEdit(layout_id, {
        layout_id,
        layerVisibility,
        responseMode: "url",
      });
      
      if (result.code === 200) {
        alert("保存成功！");
        setHasChanges(false);
      } else {
        throw new Error(result.message || "保存失败");
      }
    } catch (error) {
      console.error("保存编辑失败:", error);
      alert("保存失败: " + (error instanceof Error ? error.message : "未知错误"));
    }
  };

  /**
   * 触发3D模型生成
   */
  const handleGenerate3D = async () => {
    if (hasChanges) {
      const confirmGen = confirm("有未保存的更改，是否先保存再生成3D？");
      if (confirmGen) {
        await handleSaveEdit();
      }
    }
    
    setIsGenerating3D(true);
    setGeneration3DProgress(0);
    setGeneration3DStatus("初始化...");

    try {
      setGeneration3DStatus("发送生成请求...");
      setGeneration3DProgress(10);

      const result = await generate3DModel(layout_id);

      if (result.code !== 200 || !result.data) {
        throw new Error(result.message || "生成3D模型失败");
      }

      const data = result.data;
      setGeneration3DProgress(20);
      setGeneration3DStatus("后端生成中...");

      // 轮询进度
      if (data.taskId) {
        let completed = false;
        let retries = 0;
        const maxRetries = 120;

        while (!completed && retries < maxRetries) {
          await new Promise((resolve) => setTimeout(resolve, 1000));
          retries++;

          try {
            const progressResult = await getLayoutProgress(data.taskId);
            
            if (progressResult.code === 200 && progressResult.data) {
              setGeneration3DProgress(progressResult.data.progress || 50);
              setGeneration3DStatus(progressResult.data.message || "生成中...");

              if (progressResult.data.progress >= 100) {
                completed = true;
              }
            }
          } catch (progressError) {
            console.warn("获取进度失败:", progressError);
          }
        }

        if (!completed) {
          throw new Error("生成超时（120秒）");
        }
      }

      setGeneration3DProgress(100);
      setGeneration3DStatus(
        `生成完成！共 ${data.objCount || 0} 个OBJ文件`
      );

      setTimeout(() => {
        setIsGenerating3D(false);
        setGeneration3DStatus("");
      }, 2000);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "未知错误";
      setGeneration3DStatus(`错误: ${errorMsg}`);
      console.error("3D生成失败:", error);

      setTimeout(() => {
        setIsGenerating3D(false);
        setGeneration3DStatus("");
      }, 3000);
    }
  };

  const handleZoomIn = () => setZoom((z) => Math.min(z + 10, 200));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 10, 50));
  const handleZoomReset = () => {
    setZoom(100);
    setPan({ x: 0, y: 0 });
  };

  const handlePanStart = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (event.button !== 0) return;
    isPanningRef.current = true;
    panStartRef.current = {
      x: event.clientX,
      y: event.clientY,
      panX: pan.x,
      panY: pan.y,
    };
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handlePanMove = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (!isPanningRef.current) return;
    const dx = event.clientX - panStartRef.current.x;
    const dy = event.clientY - panStartRef.current.y;
    setPan({
      x: panStartRef.current.panX + dx,
      y: panStartRef.current.panY + dy,
    });
  };

  const handlePanEnd = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (!isPanningRef.current) return;
    isPanningRef.current = false;
    event.currentTarget.releasePointerCapture(event.pointerId);
  };

  return (
    <div className="grid h-full w-full gap-3 rounded-[12px] border border-[var(--border)] bg-[var(--surface)] p-3">
      {/* 工具栏 */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded-[10px] border border-[var(--border)] bg-[var(--surface-2)] px-2 py-1">
        <div className="flex flex-wrap items-center gap-2">
          <button onClick={handleZoomOut} className={`${buttonBase} ${buttonSmall}`}>
            缩小 -
          </button>
          <button onClick={handleZoomReset} className={`${buttonBase} ${buttonSmall}`}>
            重置
          </button>
          <button onClick={handleZoomIn} className={`${buttonBase} ${buttonSmall}`}>
            放大 +
          </button>
          <span className="min-w-[44px] text-center text-[11px] font-semibold text-[var(--muted)]">{zoom}%</span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {hasChanges && (
            <button
              onClick={handleSaveEdit}
              className={`${buttonBase} ${buttonSmall} ${buttonPrimary}`}
              title="保存编辑（更新服务器JSON/SVG）"
            >
              💾 保存编辑
            </button>
          )}
          
          <button
            onClick={handleGenerate3D}
            disabled={isGenerating3D}
            className={`${buttonBase} ${buttonSmall} ${buttonDanger}`}
            title="使用当前编辑生成3D模型"
          >
            {isGenerating3D ? "⏳ 生成中..." : "🚀 生成3D模型"}
          </button>
        </div>
      </div>

      {/* 进度显示 */}
      {isGenerating3D && (
        <div className="mt-3 grid gap-2 rounded-[10px] border border-[var(--border)] bg-[var(--surface-2)] p-3 text-[12px]">
          <div className="text-[12px] text-[var(--muted)]">{generation3DStatus}</div>
          <div className="h-2.5 w-full overflow-hidden rounded-full bg-[var(--surface)]">
            <div
              className="h-full bg-[linear-gradient(90deg,var(--accent),var(--accent-2))] transition-[width] duration-300"
              style={{ width: `${generation3DProgress}%` }}
            />
          </div>
          <div className="text-[11px] text-[var(--muted)]">{generation3DProgress}%</div>
        </div>
      )}

      {/* 主编辑区域 */}
      <div className="mt-3 grid gap-3 lg:grid-cols-[minmax(0,1fr)_280px]">
        {/* SVG显示区域 - 直接显示后端生成的SVG */}
        <div
          className="relative min-h-[240px] overflow-hidden rounded-[12px] border border-[var(--border)] bg-[var(--surface)]"
          onPointerDown={handlePanStart}
          onPointerMove={handlePanMove}
          onPointerUp={handlePanEnd}
          onPointerLeave={handlePanEnd}
        >
          <div
            className="origin-top-left"
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom / 100})`,
              transformOrigin: "top left",
            }}
          >
            <object
              data={svgUrl}
              type="image/svg+xml"
              width={width}
              height={height}
              style={{
                border: "1px solid #ccc",
                backgroundColor: "#fff",
                display: "block",
              }}
            >
              <img src={svgUrl} alt="SVG Layout" width={width} height={height} />
            </object>
          </div>
        </div>

        {/* 图层控制面板 */}
        {layers.length > 0 && (
          <div className="grid gap-3 rounded-[12px] border border-[var(--border)] bg-[var(--surface)] p-3 text-[12px]">
            <h3 className="m-0 text-[13px] font-semibold">图层控制</h3>
            <div className="grid gap-2">
              {layers.map((layer) => (
                <div key={layer.id} className="rounded-lg border border-[var(--border)] bg-[var(--surface-2)] px-2 py-1">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={layerVisibility[layer.id] !== false}
                      onChange={() => toggleLayerVisibility(layer.id)}
                    />
                    <span className="text-[12px]">{layer.name}</span>
                  </label>
                </div>
              ))}
            </div>
            
            <div className="rounded-lg border border-dashed border-[var(--border)] bg-[var(--surface-2)] p-2 text-[11px] text-[var(--muted)]">
              <p>💡 提示：勾选/取消图层可见性</p>
              <p>📝 编辑后点击"保存编辑"更新服务器文件</p>
              <p>🚀 保存后即可生成3D模型</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
